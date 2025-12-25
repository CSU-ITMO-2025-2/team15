import logging

import pika
from decouple import config
from ml.const import RABBIT_HOST, RABBIT_PORT, RABBIT_USER, RABBIT_PASSWORD, RABBIT_URI_PARAM, RABBIT_QUEUE

logger = logging.getLogger(__name__)

# 1. ИСПРАВЛЕНИЕ: cast=int
# config() возвращает строку, а pika ждет число (int) для порта.
# Без этого будет TypeError.
rabbitmq_params = pika.ConnectionParameters(
    host=config(RABBIT_HOST),
    port=config(RABBIT_PORT, cast=int),
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=config(RABBIT_USER),
        password=config(RABBIT_PASSWORD)
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)


def send_message2rabbit(message: str):
  try:
    # 2. ИСПРАВЛЕНИЕ: Передаем объект rabbitmq_params
    with pika.BlockingConnection(rabbitmq_params) as connection:
      channel = connection.channel()
      queue_name = RABBIT_QUEUE

      channel.queue_declare(queue=queue_name, durable=False)

      channel.basic_publish(
          exchange='',
          routing_key=queue_name,
          body=message.encode('utf-8'),
          properties=pika.BasicProperties(
              delivery_mode=pika.DeliveryMode.Persistent,
              content_type='text/plain'
          )
      )
      logger.info(f"Сообщение отправлено в {queue_name}")

  except pika.exceptions.UnroutableError:
    logger.error("Сообщение не может быть доставлено (нет маршрута)")
  except pika.exceptions.AMQPError as e:
    logger.error(f"Ошибка RabbitMQ: {e}")
  except Exception as e:
    logger.error(f"Непредвиденная ошибка: {e}")
