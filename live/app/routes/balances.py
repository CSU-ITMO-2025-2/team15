from fastapi import APIRouter, Depends, HTTPException, status
from auth.authenticate import authenticate
from component import balance_component as BalanceComponent
from component import user_component as UserComponent

from routes.dto.BalanceDto import BalanceDto

balance_router = APIRouter(tags=["Balance"])

BALANCE_DOESNT_EXIST = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Balance ID does not exist",
)


@balance_router.get("/{id}", response_model=BalanceDto)
async def check_balance_by_user(user: str = Depends(authenticate)) -> BalanceDto:
    user = UserComponent.get_user_by_login(user)
    balance = BalanceComponent.load_balance(user.id)

    if balance:
        return BalanceDto.from_orm(balance)
    raise BALANCE_DOESNT_EXIST


@balance_router.post("/replenish/{amount}")
async def replenish_balance(
        amount: float,
        user: str = Depends(authenticate)
):
    user = UserComponent.get_user_by_login(user);
    BalanceComponent.add_balance(user.id, amount)

    return {"message": "Balance replenished successfully"}
