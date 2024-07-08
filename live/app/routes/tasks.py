from fastapi import APIRouter, Depends, HTTPException, status
# from auth.au import authenticate
from component import task_compoenent as TaskComponent, user_component as UserComponent
from component import transaction_component as TransactionComponent
from routes.dto.TaskDto import TaskDto, HistoryDto

from auth.authenticate import authenticate

task_router = APIRouter(tags=["Task"])


@task_router.get("/{id}", response_model=TaskDto)
async def get_task(id: int) -> TaskDto:
    task = TaskComponent.get_task(id)
    if task:
        return TaskDto.from_task(task)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task does not exist",
    )


@task_router.post("/create/data/{dataid}/model/{modelid}")
async def execute_task(
        dataid: int,
        modelid: int = 1,
        user: str = Depends(authenticate)
):
    TaskComponent.add_task(
        task_type="wine-score",
        userid=UserComponent.get_user_by_login(user).id,
        dataid=dataid,
        modelid=modelid,
        status="init"
    )
    return {"message": f"Task {id} is running"}


@task_router.post("/execute/{id}")
async def execute_task(
        id: int
):
    TaskComponent.run(id)
    return {"message": f"Task {id} is running"}


@task_router.get("/history/{user_id}")
async def task_history(
        task_id: int,
        user: str = Depends(authenticate)
) -> list[HistoryDto]:
    history = []
    transactions = TransactionComponent.get_by_taskid(task_id)
    for tr in transactions:
        history.append(HistoryDto(
            id=tr.id,
            status=tr.operationType,
            datetime=tr.datetime
        ))

    return history
