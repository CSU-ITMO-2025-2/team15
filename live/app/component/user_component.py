from database.database import get_session
from models.model import User


def get_user_by_id(id: int) -> User:
    with get_session() as session:
        return session.query(User).where(User.id == id).one_or_none()


def get_user_by_login(login: str) -> User:
    with get_session() as session:
        return session.query(User).where(User.login == login).one_or_none()


def get_user_email(email: str) -> User:
    with get_session() as session:
        return session.query(User).where(User.email == email).one_or_none()


def __add_user(login: str, email: str, user_type: str, password: str):
    with get_session() as session:
        user = User(login=login, email=email, role=user_type, password=password)
        session.add(user)
        session.commit()


def add_admin(login: str, email: str, password: str):
    __add_user(login=login, email=email, user_type="admin", password=password)


def add_client(login: str, email: str, password: str):
    __add_user(login=login, email=email, user_type="client", password=password)
