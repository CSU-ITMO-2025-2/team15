import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
# from auth.au import authenticate
from component import task_compoenent as TaskComponent, user_component as UserComponent, data_component, \
    history_component, user_component
from component import transaction_component as TransactionComponent
from routes.dto.TaskDto import TaskDto, HistoryDto

from auth.authenticate import authenticate

history_router = APIRouter(tags=["Hisotry"])


@history_router.get("/all/")
async def task_history(
        user: str = Depends(authenticate)
) -> list[HistoryDto]:
    response = []

    user = user_component.get_user_by_login(user)
    history = history_component.get_all(user.id)
    for value in history:
        response.append(HistoryDto(
            id=value.id,
            operation=value.operation_type,
            datetime=str(value.datetime)
        ))

    return response
