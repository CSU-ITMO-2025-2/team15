from fastapi import APIRouter, Depends, HTTPException, status

from auth.authenticate import authenticate
from component import data_component as DataComponent
from component import user_component as UserComponent
from routes.dto.AnlData import WineInput
import pandas as pd

dataframe_router = APIRouter(tags=["Dataframe"])


@dataframe_router.get("/{id}")
async def get_dataframe(id: int) -> list[WineInput]:
    datainfo = DataComponent.get(id)
    data = pd.read_csv(datainfo.path2data)

    recs = []
    for i, value in data.iterrows():
        recs.append(
            WineInput(
                fixed_acidity=value["fixed_acidity"],
                volatile_acidity=value["volatile_acidity"],
                citric_acid=value["citric_acid"],
                residual_sugar=value["residual_sugar"],
                chlorides=value["chlorides"],
                free_sulfur_dioxide=value["free_sulfur_dioxide"],
                total_sulfur_dioxide=value["total_sulfur_dioxide"],
                density=value["density"],
                pH=value["pH"],
                sulphates=value["sulphates"],
                alcohol=value["alcohol"]
            )
        )

    return recs


@dataframe_router.post("/upload/")
async def upload_dataframe(data: WineInput,
                           user: str = Depends(authenticate)):
    v_results = data.validate_data()
    if v_results:
        return {"message": f"Validation errors {v_results}"}

    user = UserComponent.get_user_by_login(user)

    df = pd.DataFrame.from_dict(data.model_dump())
    DataComponent.save(df, user.id)

    return {"message": f"Dataframe has been added"}


@dataframe_router.delete("/{id}")
async def delete_df(
        id: int,
        user: str = Depends(authenticate)
) -> dict:
    try:
        DataComponent.delete(dataid=id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User DF with supplied ID does not exist",
        )

    return {"message": "User DF deleted successfully"}
