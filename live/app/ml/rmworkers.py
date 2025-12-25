import base64
import io
import logging
import pickle

import pandas as pd
import pika
# Импорты твоих компонентов
# noinspection PyPackageRequirements
from component import (
  model_component as ModelComponent,
  user_component as UserCompoenent,
  data_component as DataComponent,
  task_compoenent as TaskCompoenent,
  history_component
)
from decouple import config
from ml.const import RABBIT_HOST, RABBIT_PORT, RABBIT_USER, RABBIT_PASSWORD, \
  RABBIT_QUEUE
from ml.dto.PredictionRequest import PredictionRequest
from pika.adapters.blocking_connection import BlockingChannel
from pydantic import ValidationError
from sqlmodel import Session

from database.database import get_session_context

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLWorker:
  def __init__(self):
    self.connection_params = pika.ConnectionParameters(
        host=config(RABBIT_HOST),
        port=config(RABBIT_PORT),
        virtual_host='/',
        credentials=pika.PlainCredentials(
            username=config(RABBIT_USER),
            password=config(RABBIT_PASSWORD)
        ),
        # Увеличенный heartbeat для долгих ML-операций
        heartbeat=600,
        blocked_connection_timeout=300
    )
    self.model_cache = {}

  def _get_model(self, model_name: str, session: Session):
    model_entity = ModelComponent.get_model_by_name(model_name, session)
    logger.info(f"Loading model {model_name} from {model_entity.path2model}")
    with open(model_entity.path2model, 'rb') as file:
      return pickle.load(file)

  def process_prediction(self, request: PredictionRequest, session: Session):
    model = self._get_model(request.namemodel, session)

    # 1. Берем строку Base64 прямо из запроса (это строка, не байты!)
    encoded_string = request.path2data

    # 2. Декодируем Base64 обратно в бинарный вид (исходный файл)
    # base64.b64decode отлично кушает обычные строки
    decoded_file_content = base64.b64decode(encoded_string)

    # 3. Превращаем байты в файловый объект для pandas
    csv_buffer = io.BytesIO(decoded_file_content)

    # 4. Читаем
    df = pd.read_csv(csv_buffer)

    prediction_array = model.predict(df)
    return pd.DataFrame(prediction_array, columns=["result"])

  def save_process_results(self, task_id: int, result_df: pd.DataFrame,
      session: Session):
    """Сохранение результатов в БД"""
    task = TaskCompoenent.get_task(task_id, session)
    if not task:
      logger.error(f"Task {task_id} not found in DB")
      return

    user = UserCompoenent.get_user_by_id(task.userid, session)

    # Сохраняем файл результата
    fullpath2result = DataComponent.save_results(result_df, user.id, session)
    data = DataComponent.get_by_path(str(fullpath2result), session)

    # Обновляем связи
    TaskCompoenent.set_result(task_id, data.id, session)

    # Списываем баланс
    # balance_component.write_off(data.userid, 50.0, session)

    # Пишем историю
    history_component.push(
        task.userid,
        "write off for prediction",
        session,
        "write off 50.0 RUB for prediction quality",
    )

    # Финализируем задачу (меняем статус на DONE)
    TaskCompoenent.final(task_id, session)

    history_component.push(
        task.userid,
        "finish task",
        session,
        f"Task {task_id} is done"
    )

  def on_message(self, ch: BlockingChannel, method, properties, body):
    """Обработчик сообщения"""
    try:
      message_body = body.decode('utf-8')
      logger.info(f"Processing message: {method.delivery_tag}")

      # 1. Валидация Pydantic
      try:
        request = PredictionRequest.model_validate_json(message_body)
      except ValidationError as e:
        logger.error(f"Invalid message format: {e}")
        # Если формат кривой, обрабатывать нет смысла -> удаляем из очереди
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

      # 2. Основной цикл работы с БД
      with get_session_context() as session:
        try:
          # Выполняем ML
          result_df = self.process_prediction(request, session)

          # Сохраняем в БД (все транзакции внутри этого метода используют одну сессию)
          self.save_process_results(request.task_id, result_df, session)

          # Фиксируем изменения в базе
          session.commit()
          logger.info(f"Task {request.task_id} completed successfully")

        except Exception as db_err:
          session.rollback()
          logger.error(
              f"Database/Logic error for Task {request.task_id}: {db_err}")

          # ! ВАЖНО: Тут желательно добавить логику пометки задачи как FAILED в БД,
          # чтобы пользователь не ждал вечно. Например:
          # TaskComponent.set_status(request.task_id, "ERROR", session)
          # session.commit()

          # Пока просто логируем и идем дальше.
          raise db_err

      # 3. Подтверждаем RabbitMQ, что задача выполнена
      ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
      logger.critical(f"Unexpected error processing message: {e}",
                      exc_info=True)
      # Даже при ошибке делаем Ack, чтобы не зациклить обработку "битого" сообщения.
      # В идеальном мире такие сообщения нужно отправлять в Dead Letter Exchange (DLX).
      ch.basic_ack(delivery_tag=method.delivery_tag)

  def start(self):
    """Запуск воркера с реконнектом"""
    while True:
      try:
        logger.info("Connecting to RabbitMQ...")
        connection = pika.BlockingConnection(self.connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=RABBIT_QUEUE, durable=False)

        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=RABBIT_QUEUE,
            on_message_callback=self.on_message,
            auto_ack=False
        )

        logger.info("Worker started. Consuming...")
        channel.start_consuming()

      except pika.exceptions.AMQPConnectionError as e:
        logger.warning(f"Connection lost: {e}. Retrying in 5s...")
        import time
        time.sleep(5)
      except Exception as e:
        logger.error(f"Critical worker crash: {e}. Restarting in 5s...")
        import time
        time.sleep(5)


if __name__ == "__main__":
  worker = MLWorker()
  worker.start()
