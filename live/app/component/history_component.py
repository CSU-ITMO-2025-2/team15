from database.database import get_session
from models.model import Data, History


def get_all(user_id: int) -> list[History]:
    with get_session() as session:
        return session.query(History).where((History.userid == user_id)).all()


def push(user_id: int, operation: str, details: str = None):
    with get_session() as session:
        session.add(History(userid=user_id, operation_type=operation, details=details))
        session.commit()
