from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from utils import transaction
from auth.authenticate import authenticate
from component import balance_component as BalanceComponent
from component import user_component as UserComponent
from database.database import get_session
from routes.dto.BalanceDto import BalanceDto

balance_router = APIRouter(tags=["Balance"])

BALANCE_DOESNT_EXIST = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Balance ID does not exist",
)


@transaction
@balance_router.get("/{id}", response_model=BalanceDto)
async def check_balance_by_user(user: str = Depends(authenticate),
    session=Depends(get_session)) -> BalanceDto:
  user = UserComponent.get_user_by_login(user, session=session)
  balance = BalanceComponent.load_balance(user.id, session=session)

  if not balance:
    BalanceComponent.add_balance(userid=user.id, amount=0.0, session=session)
    balance = BalanceComponent.load_balance(userid=user.id, session=session)

  return BalanceDto(
      userId=user.id,
      value=balance.value
  )


@transaction
@balance_router.post("/replenish/{amount}")
async def replenish_balance(
    amount: float,
    user: str = Depends(authenticate),
    session: Session = Depends(get_session)
):
  user = UserComponent.get_user_by_login(user, session=session)
  BalanceComponent.add_balance(user.id, amount, session=session)

  return {"message": "Balance replenished successfully"}
