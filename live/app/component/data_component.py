from pandas import DataFrame
from live.app.database.database import get_session
from live.app.models.model import Data


def upload_data(data: DataFrame):
    with get_session() as session:
        data = Data(data)
        session.save(data)
        session.commit()


def get(dataid: int):
    with get_session() as session:
        return session.query(Data).where(Data.id == dataid).one_or_none()
