from pandas import DataFrame
from database.database import get_session
from models.model import Data


def upload_data(path2data: str):
    with get_session() as session:
        data = Data(path2data=path2data)
        session.add(data)
        session.commit()


def get(dataid: int):
    with get_session() as session:
        return session.query(Data).where(Data.id == dataid).one_or_none()
    
def get_by_path(full_filename: str):
    with get_session() as session:
        return session.query(Data).where(Data.path2data == full_filename).one_or_none()
