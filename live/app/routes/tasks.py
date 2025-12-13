from auth.authenticate import authenticate
from component import task_compoenent as TaskComponent, \
  user_component as UserComponent, data_component, \
  history_component, user_component
from database.database import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from routes.dto.TaskDto import TaskDto
from sqlmodel import Session
from utils import transaction

task_router = APIRouter(tags=["Task"])


@transaction
@task_router.get("/{id}", response_model=TaskDto)
async def get_task(id: int,
    session: Session = Depends(get_session)
) -> TaskDto:
  task = TaskComponent.get_task(id, session=session)
  if task:
    return TaskDto.from_task(task)
  raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Task does not exist",
  )


@transaction
@task_router.get("/all/", response_model=list[TaskDto])
async def get_tasks(
    login: str = Depends(authenticate),
    session: Session = Depends(get_session)
) -> list[TaskDto]:
  user = UserComponent.get_user_by_login(login, session=session)
  tasks = TaskComponent.get_tasks(user.id, session=session)

  res = []
  for task in tasks:
    original_data_path = \
      data_component.get(task.dataid, session=session).path2data.split("/")[-1]
    results = None
    if task.result_id:
      results = data_component.get(task.result_id, session=session).path2data
      # results = str(pd.read_csv(result_path).iloc[0].values[0])

    res.append(
        TaskDto(id=task.id,
                status=task.status,
                datapath=original_data_path,
                predicted_value=results)
    )
  return res


@transaction
@task_router.post("/create/data/{dataid}/model/{modelid}/")
async def create_task(
    dataid: int,
    modelid: int,
    user: str = Depends(authenticate),
    session: Session = Depends(get_session)
) -> dict:
  TaskComponent.add_task(
      task_type="wine-score",
      userid=UserComponent.get_user_by_login(user, session=session).id,
      dataid=dataid,
      modelid=modelid,
      status="init",
      session=session
  )

  history_component.push(
      user_component.get_user_by_login(user, session=session).id, "create task", session,
      f"create task to handle data {dataid} by model {modelid}")

  return {"message": f"Task is running"}


@transaction
@task_router.post("/execute/{id}/")
async def execute_task(
    id: int,
    user: str = Depends(authenticate),
    session: Session = Depends(get_session)
):
  TaskComponent.run(id, session)
  history_component.push(
      user_component.get_user_by_login(user, session=session).id,
      "execute task",
      session,
      f"execute task {id}")
  return {"message": f"Task {id} is running"}
