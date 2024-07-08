import uuid

import pika
import threading

from decouple import config
from pandas import DataFrame
from pydantic import ValidationError
import pickle
import pandas as pd

from component import model_component as ModelComponent, task_compoenent as TaskCompoenent, \
    user_component as UserCompoenent, data_component as DataComponent

from ml.dto.PredictionRequest import PredictionRequest

RABBIT_URI_PARAM = "RABBITMQ_CONNECTION_URI"
RABBIT_QUEUE = "inbound_requests"
RABBIT_HOST = "RABBIT_HOST"
RABBIT_PORT = "RABBIT_PORT"
RABBIT_USER = "RABBIT_USER"
RABBIT_PASSWORD = "RABBIT_PASSWORD"

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


def prepare_data(ch, method, properties, body):
    try:
        data = body.decode('utf-8')
        request = PredictionRequest.model_validate_json(data)

        make_prediction(ch, method, properties, request)
    except ValidationError as e:
        response = f"Invalid data: {e}"
        correlation_id = properties.correlation_id
        reply_to = properties.reply_to
        ch.basic_publish(
            exchange='',
            routing_key=reply_to,
            properties=pika.BasicProperties(correlation_id=correlation_id),
            body=response
        )


def make_prediction(ch, method, properties, model_input: PredictionRequest):
    if model_input.namemodel not in MODEL_CACHE:
        model_entity = ModelComponent.get_model_by_name(model_input.namemodel)

        with open(model_entity.path2model, 'rb') as file:
            model = pickle.load(file)
            MODEL_CACHE[model_input.namemodel] = model

    df = pd.read_csv(model_input.path2data)
    result = MODEL_CACHE[model_input.namemodel].predict(df)

    save_results(ch, method, properties, model_input.task_id, result)


def save_results(ch, method, properties, taskid: int, result: DataFrame):
    task = TaskCompoenent.get_task(taskid)
    user = UserCompoenent.get_user_by_id(task.userid)

    fullpath2result = DataComponent.save(result, user.id)
    data = DataComponent.get_by_path(fullpath2result)

    TaskCompoenent.set_result(taskid, data.id)
    TaskCompoenent.final(taskid)

    return_results(ch, method, properties)


def return_results(ch, method, properties):
    correlation_id = properties.correlation_id
    reply_to = properties.reply_to

    ch.basic_publish(
        exchange='',
        routing_key=reply_to,
        properties=pika.BasicProperties(correlation_id=correlation_id),
        body={"message": "quality prediction is done"}
    )


def callback(ch, method, properties, body):
    prepare_data(ch, method, properties, body)


def worker():
    connection = pika.BlockingConnection(rabbitmq_connection_string)
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_QUEUE)
    channel.basic_consume(queue=RABBIT_QUEUE, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


for i in range(3):
    threading.Thread(target=worker).start()
