import base64
from datetime import datetime

from component import data_component, model_component
from ml.dto.PredictionRequest import PredictionRequest
from ml.rabbitapi import send_message2rabbit
from models.model import Task
from sqlmodel import Session


def add_task(
    userid: int,
    dataid: int,
    modelid: int,
    session: Session,
    transaction_id: int = None,
    status: str = "wait",
    task_type: str = "default",
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
    session: Session) -> Task:
  return session.query(Task).where(Task.id == task_id).one_or_none()


def get_tasks(user_id: int,
    session: Session) -> list[Task]:
  return session.query(Task).where((Task.userid == user_id) &
                                   (Task.status == "init")).all()


def set_result(taskid: int, value: float,
    session: Session):
  new_state = {'result_id': value}
  session.query(Task).where(Task.id == taskid).update(new_state)
  session.commit()


def set_status(taskid: int, status: str,
    session: Session):
  new_state = {'status': status}
  session.query(Task).where(Task.id == taskid).update(new_state)


def run(taskid: int, session: Session):
  task = get_task(task_id=taskid, session=session)
  data = data_component.get(task.dataid, session=session)
  model = model_component.get_model(task.modelid, session=session)

  if True:
    # with open(data.path2data, "rb") as file:
    #  file_content = file.read()

    # 2. Кодируем содержимое в base64 (на выходе будут байты b'...')
    csv_bytes = data.path2data.encode('utf-8')  # str -> bytes
    encoded_bytes = base64.b64encode(csv_bytes)

    request = PredictionRequest(
        path2data=encoded_bytes,
        namemodel=model.modelname,
        task_id=str(taskid)
    )

    send_message2rabbit(request.model_dump_json())
  else:
    print("file not found", data.path2data)


def final(taskid: int,
    session: Session):
  new_state = {'status': "finished", 'processing_end': datetime.now()}
  session.query(Task).where(Task.id == taskid).update(new_state)
  session.commit()
