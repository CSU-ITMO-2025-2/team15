from live.app.models.model import User
from live.app.database.database import session


def get_user_by_id(id: int):
    with session() as session:
        return session.query(User).where(User.id == id)


def get_user_login(login: str):
    with session() as session:
        return session.query(User).where(User.login == login)


def get_user_email(email: str) -> User:
    with session() as session:
        return session.query(User).where(User.email == email)


def __add_user(login: str, email: str, user_type: str):
    with session() as session:
        user = User(login=login, email=email, type=user_type)
        session.begin()
        session.save(user)
        session.commit()


def add_admin(login: str, email: str):
    __add_user(login=login , email=email, user_type="admin")


def add_client(login: str, email: str):
    __add_user(login=login , email=email, user_type="client")
