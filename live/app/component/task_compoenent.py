from sqlmodel import Session

from database.database import get_session
from models.model import Task
from datetime import datetime

from component import data_component, model_component
from ml.dto.PredictionRequest import PredictionRequest
from ml.rabbitapi import send_message2rabbit


def add_task(
        userid: int,
        dataid: int,
        modelid: int,
        transaction_id: int = None,
        status: str = "wait",
        task_type: str = "default",
        session: Session = get_session()
):
    task = Task(
        task_type=str(task_type),
        transaction_id=transaction_id,
        userid=int(userid),
        dataid=int(dataid),
        modelid=int(modelid),
        status=str(status),
        processing_end=None,
        processing_start=None
    )

    session.add(task)
    session.commit()


def get_task(task_id: int,
             session: Session = get_session()) -> Task:
    return session.query(Task).where(Task.id == task_id).one_or_none()


def get_tasks(user_id: int,
              session: Session = get_session()) -> list[Task]:
    return session.query(Task).where(Task.userid == user_id).all()


def set_result(taskid: int, value: float,
               session: Session = get_session()):
    new_state = {'result_id': value}
    session.query(Task).where(Task.id == taskid).update(new_state)
    session.commit()


def set_status(taskid: int, status: str,
               session: Session = get_session()):
    new_state = {'status': status}
    session.query(Task).where(Task.id == taskid).update(new_state)


def run(taskid: int):
    task = get_task(task_id=taskid)
    data = data_component.get(task.dataid)
    model = model_component.get_model(task.modelid)

    request = PredictionRequest(
        path2data=data.path2data,
        namemodel=model.modelname,
        task_id=str(taskid)
    )

    send_message2rabbit(request.model_dump_json())


def final(taskid: int,
          session: Session = get_session()):
    new_state = {'status': "finished", 'processing_end': datetime.now()}
    session.query(Task).where(Task.id == taskid).update(new_state)
    session.commit()
