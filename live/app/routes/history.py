import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from utils import transaction
# from auth.au import authenticate
from component import task_compoenent as TaskComponent, user_component as UserComponent, data_component, \
    history_component, user_component
from component import transaction_component as TransactionComponent
from database.database import get_session
from routes.dto.TaskDto import TaskDto, HistoryDto

from auth.authenticate import authenticate

history_router = APIRouter(tags=["Hisotry"])

@transaction
@history_router.get("/all/")
async def task_history(
        user: str = Depends(authenticate),
        session: Session = Depends(get_session)
) -> list[HistoryDto]:
    response = []

    user = user_component.get_user_by_login(user, session=session)
    history = history_component.get_all(user.id, session=session)
    for value in history:
        response.append(HistoryDto(
            id=value.id,
            operation=value.operation_type,
            datetime=str(value.datetime)
        ))

    return response
