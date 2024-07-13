from database.database import get_session;
from models.model import Balance


def add_balance(userid: int, amount: float):
    with get_session() as session:
        curren_balance = session.query(Balance).where(Balance.userId == userid).one_or_none()
        if curren_balance:
            session.query(Balance).where(Balance.userId == userid).update({'value': curren_balance.value + amount})
            session.commit()
        else:
            session.add(Balance(userid, amount))
            session.commit()


def load_balance(userid: int) -> Balance:
    with get_session() as session:
        return session.query(Balance).where(Balance.userId == userid).one_or_none()


def write_off(userid: int, amount: float):
    with get_session() as session:
        curren_balance = session.query(Balance).where(Balance.userId == userid).one_or_none()
        if curren_balance:
            session.query(Balance).where(Balance.userId == userid).update({'value': curren_balance.value - amount})
            session.commit()

        else:
            session.add(Balance(userid, -amount))
            session.commit()
