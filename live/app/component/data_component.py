import os
import uuid

from pandas import DataFrame
from database.database import get_session
from models.model import Data

BASE_PATH_2_DATA = "/data/"


def upload_data(path2data: str, userid: int):
    with get_session() as session:
        data = Data(path2data=path2data, userid=userid)
        session.add(data)
        session.commit()


def get(dataid: int) -> Data:
    with get_session() as session:
        return session.query(Data).where(Data.id == dataid).one_or_none()


def save(df: DataFrame, userId: int):
    full_file_name = f"{BASE_PATH_2_DATA}{userId}{uuid.uuid4()}"
    df.to_csv(full_file_name)

    upload_data(full_file_name, userId)


def delete(dataid: int):
    data = get(dataid)
    os.remove(data.path2data)
    with get_session() as session:
        session.delete(data)
        session.commit()


def get_by_path(full_filename: str) -> Data:
    with get_session() as session:
        return session.query(Data).where(Data.path2data == full_filename).one_or_none()
