import os
import uuid

from decouple import config
from pandas import DataFrame
from sqlmodel import Session

from database.database import get_session
from ml.const import DATA_ROOT_PATH
from models.model import Data

BASE_PATH_2_DATA = config(DATA_ROOT_PATH)


def upload_data(path2data: str, userid: int, display: int = 1, session: Session = get_session()) -> Data:
    data = Data(path2data=path2data, userid=userid, display=display)
    session.add(data)
    session.commit()


def get(data_id: int, session: Session = get_session()) -> Data:
    return session.query(Data).where(Data.id == data_id).one_or_none()


def get_all(user_id: int, session: Session = get_session()) -> list[Data]:
    return session.query(Data).where((Data.userid == user_id) & (Data.display == 1))


def save(df: DataFrame, userId: int, session: Session = get_session(), root_path: str = BASE_PATH_2_DATA) -> str:
    if not os.path.exists(f"{root_path}"):
        os.mkdir(f"{root_path}")

    if not os.path.exists(f"{root_path}/{userId}"):
        os.mkdir(f"{root_path}/{userId}")

    full_file_name = f"{root_path}/{userId}/{uuid.uuid4()}.csv"
    df.to_csv(full_file_name, index=False)

    upload_data(full_file_name, userId, session=session)
    return full_file_name


def save_results(df: DataFrame, userId: int, session: Session = get_session(),
                 root_path: str = BASE_PATH_2_DATA) -> str:
    if not os.path.exists(f"{root_path}/{userId}"):
        os.mkdir(f"{root_path}/{userId}")

    full_file_name = f"{root_path}/{userId}/{uuid.uuid4()}.csv"
    df.to_csv(full_file_name, index=False)

    upload_data(full_file_name, userId, display=0, session=session)
    return full_file_name


def delete(dataid: int, session: Session = get_session()):
    data = get(dataid, session=session)

    if os.path.exists(data.path2data):
        os.remove(data.path2data)

    session.query(Data).filter(Data.id == dataid).delete()
    session.commit()


def get_by_path(full_filename: str, session: Session = get_session()) -> Data:
    return session.query(Data).where(Data.path2data == full_filename).one_or_none()
