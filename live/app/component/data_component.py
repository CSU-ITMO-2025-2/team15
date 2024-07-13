import os
import uuid

from pandas import DataFrame
from database.database import get_session
from models.model import Data

BASE_PATH_2_DATA = "/data/"


def upload_data(path2data: str, userid: int, display: int = 1):
    with get_session() as session:
        data = Data(path2data=path2data, userid=userid, display=display)
        session.add(data)
        session.commit()


def get(data_id: int) -> Data:
    with get_session() as session:
        return session.query(Data).where(Data.id == data_id).one_or_none()


def get_all(user_id: int) -> list[Data]:
    with get_session() as session:
        print("get_all")
        return session.query(Data).where((Data.userid == user_id) & (Data.display == 1))


def save(df: DataFrame, userId: int) -> str:
    if not os.path.exists(f"{BASE_PATH_2_DATA}/{userId}"):
        os.mkdir(f"{BASE_PATH_2_DATA}/{userId}")

    full_file_name = f"{BASE_PATH_2_DATA}/{userId}/{uuid.uuid4()}.csv"
    df.to_csv(full_file_name, index=False)

    upload_data(full_file_name, userId)
    return full_file_name


def save_results(df: DataFrame, userId: int) -> str:
    if not os.path.exists(f"{BASE_PATH_2_DATA}/{userId}"):
        os.mkdir(f"{BASE_PATH_2_DATA}/{userId}")

    full_file_name = f"{BASE_PATH_2_DATA}/{userId}/{uuid.uuid4()}.csv"
    df.to_csv(full_file_name, index=False)

    upload_data(full_file_name, userId, display=0)
    return full_file_name


def delete(dataid: int):
    data = get(dataid)

    if os.path.exists(data.path2data):
        os.remove(data.path2data)

    with get_session() as session:
        session.query(Data).filter(Data.id == dataid).delete()
        session.commit()


def get_by_path(full_filename: str) -> Data:
    with get_session() as session:
        return session.query(Data).where(Data.path2data == full_filename).one_or_none()
