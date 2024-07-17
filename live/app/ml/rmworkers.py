import uuid

import pika
import threading

from decouple import config
from pandas import DataFrame
from pydantic import ValidationError
import pickle
import pandas as pd
from sqlmodel import Session

from component import model_component as ModelComponent, \
    user_component as UserCompoenent, data_component as DataComponent, task_compoenent as TaskCompoenent, \
    balance_component, history_component
from database.database import get_session

from ml.dto.PredictionRequest import PredictionRequest

from ml.const import RABBIT_HOST, RABBIT_PORT, RABBIT_USER, RABBIT_PASSWORD, RABBIT_QUEUE

rabbitmq_connection_string = pika.ConnectionParameters(
    host=config(RABBIT_HOST),
    port=config(RABBIT_PORT),
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=config(RABBIT_USER),
        password=config(RABBIT_PASSWORD)
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)

MODEL_CACHE = {}

connection = pika.BlockingConnection(rabbitmq_connection_string)
channel = connection.channel()
channel.queue_declare(queue=RABBIT_QUEUE)


def prepare_data(ch, method, properties, body):
    try:
        data = body.decode('utf-8')
        request = PredictionRequest.model_validate_json(data)

        make_prediction(ch, method, properties, request)
    except ValidationError as e:
        correlation_id = properties.correlation_id
        reply_to = properties.reply_to
        ch.basic_publish(
            exchange='',
            routing_key=reply_to,
            properties=pika.BasicProperties(correlation_id=correlation_id),
            body=str({"message": "some problevs"})
        )


def make_prediction(ch, method, properties, model_input: PredictionRequest, session: Session = get_session()):
    if model_input.namemodel not in MODEL_CACHE:
        model_entity = ModelComponent.get_model_by_name(model_input.namemodel)

        with open(model_entity.path2model, 'rb') as file:
            model = pickle.load(file)
            MODEL_CACHE[model_input.namemodel] = model

    df = pd.read_csv(model_input.path2data)
    result = MODEL_CACHE[model_input.namemodel].predict(df)

    save_results(ch, method, properties, model_input.task_id, pd.DataFrame(result, columns=["result"]), session=session)


def save_results(ch, method, properties, taskid: int, result: DataFrame, session: Session):
    task = TaskCompoenent.get_task(taskid, session)
    user = UserCompoenent.get_user_by_id(task.userid, session)

    fullpath2result = DataComponent.save_results(result, user.id, session)
    data = DataComponent.get_by_path(fullpath2result, session)

    TaskCompoenent.set_result(taskid, data.id, session)
    balance_component.write_off(data.userid, 50.0, session)
    history_component.push(data.userid, "write off for prediction",
                           f"write off 1,0 RUB for prediction fo quality", session)
    TaskCompoenent.final(taskid, session)
    history_component.push(data.userid, "finish task",
                           f"Task {taskid} is done")

    return_results(ch, method, properties)


def return_results(ch, method, properties):
    correlation_id = properties.correlation_id
    reply_to = properties.reply_to

    ch.basic_publish(
        exchange='',
        routing_key=reply_to,
        properties=pika.BasicProperties(correlation_id=correlation_id),
        body=str({"message": "quality prediction is done"})
    )


def callback(ch, method, properties, body):
    prepare_data(ch, method, properties, body)


def start_consuming_ml():
    channel.basic_consume(
        queue=RABBIT_QUEUE,
        on_message_callback=callback,
        auto_ack=False,
    )
    print("Waiting for messages. To exit, press Ctrl+C")
    channel.start_consuming()


if __name__ == "__main__":
    start_consuming_ml()
