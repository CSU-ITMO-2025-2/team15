import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
# from auth.au import authenticate
from component import task_compoenent as TaskComponent, user_component as UserComponent, data_component, \
    history_component, user_component
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


@task_router.get("/all/", response_model=list[TaskDto])
async def get_tasks(
        login: str = Depends(authenticate)
) -> list[TaskDto]:
    user = UserComponent.get_user_by_login(login)
    tasks = TaskComponent.get_tasks(user.id)

    res = []
    for task in tasks:
        original_data_path = data_component.get(task.dataid).path2data.split("/")[-1]
        results = None
        if task.result_id:
            result_path = data_component.get(task.result_id).path2data
            results = str(pd.read_csv(result_path).iloc[0].values[0])

        res.append(
            TaskDto(id=task.id,
                    status=task.status,
                    datapath=original_data_path,
                    predicted_value=results)
        )
    return res


@task_router.post("/create/data/{dataid}/model/{modelid}/")
async def create_task(
        dataid: int,
        modelid: int,
        user: str = Depends(authenticate)
) -> dict:
    TaskComponent.add_task(
        task_type="wine-score",
        userid=UserComponent.get_user_by_login(user).id,
        dataid=dataid,
        modelid=modelid,
        status="init"
    )

    history_component.push(user_component.get_user_by_login(user).id, "create task",
                           f"create task to handle data {dataid} by model {modelid}")

    return {"message": f"Task {id} is running"}


@task_router.post("/execute/{id}/")
async def execute_task(
        id: int,
        user: str = Depends(authenticate)
):
    TaskComponent.run(id)
    history_component.push(user_component.get_user_by_login(user).id, "execute task",
                           f"execute task {id}")
    return {"message": f"Task {id} is running"}
