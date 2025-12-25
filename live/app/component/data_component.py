import os

from database.database import get_session
from decouple import config
from ml.const import DATA_ROOT_PATH
from models.model import Data
from pandas import DataFrame
from sqlmodel import Session

BASE_PATH_2_DATA = config(DATA_ROOT_PATH)


def upload_data(path2data: str, userid: int, session: Session, display: int = 1) -> Data:
  data = Data(path2data=path2data, userid=userid, display=display)
  session.add(data)
  session.commit()


def get(data_id: int, session: Session) -> Data:
  return session.query(Data).where(Data.id == data_id).one_or_none()


def get_all(user_id: int, session: Session) -> list[Data]:
  return session.query(Data).where(
      (Data.userid == user_id) & (Data.display == 1))


def save(df: DataFrame, userId: int, session: Session,
    root_path: str = BASE_PATH_2_DATA) -> str:
  if not os.path.exists(f"{root_path}"):
    os.mkdir(f"{root_path}")

  if not os.path.exists(f"{root_path}/{userId}"):
    os.mkdir(f"{root_path}/{userId}")

  # full_file_name = f"{root_path}/{userId}/{uuid.uuid4()}.csv"
  # df.to_csv(full_file_name, index=False)
  full_file_name = df.to_csv(index=False)

  upload_data(full_file_name, userId, session=session)
  return full_file_name


def save_results(df: DataFrame, userId: int, session: Session,
    root_path: str = BASE_PATH_2_DATA) -> str:
  # if not os.path.exists(f"{root_path}/{userId}"):
  # os.mkdir(f"{root_path}/{userId}")

  # full_file_name = f"{root_path}/{userId}/{uuid.uuid4()}.csv"
  # df.to_csv(full_file_name, index=False)
  upload_data(str(df.iloc[0].values[0]), userId, display=0, session=session)
  return df.iloc[0].values[0]


def delete(dataid: int, session: Session) -> str:
  data = get(dataid, session=session)
  print("delete ", data, "by", dataid)
  if os.path.exists(data.path2data):
    os.remove(data.path2data)

  session.query(Data).filter(Data.id == dataid).delete()
  session.commit()
  print("done delete ", data, "by", dataid)
  return data.path2data


def get_by_path(full_filename: str, session: Session) -> Data:
  return session.query(Data).where(
      Data.path2data == full_filename).first()
