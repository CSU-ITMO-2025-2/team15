from database.database import get_session
from models.model import Task
from datetime import datetime


def add_task(
        transaction_id: int,
        userid: int,
        dataid: int,
        modelid: int,
        status: str = "wait",
        task_type: str = "default"
):
    task = Task(
        task_type=task_type,
        transaction_id=transaction_id,
        userid=userid,
        dataid=dataid,
        modelid=modelid,
        status=status,
        processing_end=None,
        processing_start=None
    )

    with get_session() as session:
        session.add(task)
        session.commit()

def set_result(taskid: int, value: float):
    with get_session() as session:
        new_state = {'result': value}
        session.query(Task).where(Task.id == taskid).update(new_state)    
        session.commit()

def set_status(taskid: int, status: str):
    with get_session() as session:
        new_state = {'status': status}
        session.query(Task).where(Task.id == taskid).update(new_state)


def run(taskid: int):
    with get_session() as session:
        new_state = {'status': "in_progress", 'processing_start': datetime.now()}
        session.query(Task).where(Task.id == taskid).update(new_state)
        session.commit()


def final(taskid: int):
    with get_session() as session:
        new_state = {'status': "finished", 'processing_end': datetime.now()}
        session.query(Task).where(Task.id == taskid).update(new_state)
        session.commit()
