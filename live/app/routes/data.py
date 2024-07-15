from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from auth.authenticate import authenticate
from component import data_component as DataComponent, history_component, user_component
from component import user_component as UserComponent
import pandas as pd

from database.database import get_session
from ml.dto.PredictionRequest import WineParams, DataParams

dataframe_router = APIRouter(tags=["Dataframe"])


@dataframe_router.get("/{id}")
async def get_dataframe(id: int) -> list[WineParams]:
    datainfo = DataComponent.get(id)
    data = pd.read_csv(datainfo.path2data)

    recs = []
    for i, value in data.iterrows():
        recs.append(
            WineParams(
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


@dataframe_router.get("/all/", response_model=list)
async def get_dataframe(login: str = Depends(authenticate),
                        session: Session = Depends(get_session)
                        ) -> list:
    user = UserComponent.get_user_by_login(login, session)
    user_data = DataComponent.get_all(user.id, session)

    recs = []
    for value in user_data:
        recs.append(
            DataParams(
                id=value.id,
                datetime=str(value.datetime),
                path=value.path2data.split("/")[-1],
            )
        )
    return recs


@dataframe_router.post("/upload")
async def upload_dataframe(data: WineParams,
                           user: str = Depends(authenticate),
                           session: Session = Depends(get_session)
                           ):
    user = UserComponent.get_user_by_login(user, session=session)
    df = pd.DataFrame([data.model_dump()])
    datapath = DataComponent.save(df, user.id, session=session)
    data = DataComponent.get_by_path(datapath, session=session)
    history_component.push(user.id, "upload data", f"{data.path2data}", session=session)

    return {"message": f"Dataframe has been added", "id": data.id}


@dataframe_router.delete("/file/{id}")
async def delete_df(
        id: int,
        user: str = Depends(authenticate),
        session: Session = Depends(get_session)
) -> dict:
    try:
        data = DataComponent.get(data_id=id, session=session)
        DataComponent.delete(dataid=id, session=session)
        history_component.push(user_component.get_user_by_login(user, session=session).id, "delete data", f"{data.path2data}")
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User DF with supplied ID does not exist",
        )

    return {"message": "User DF deleted successfully"}
