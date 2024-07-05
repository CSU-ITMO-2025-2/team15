from live.app.database.database import get_session;
from live.app.models.model import Balance


def add_balance(userid, amount):
    with get_session() as session:
        curren_balance = session.query(Balance).where(Balance.user_id == userid).one_or_none()
        if curren_balance:
            session.query(Balance).where(Balance.user_id == userid).update({'amount': amount})
        else:
            session.save(Balance(userid, amount))
            session.commit()


def write_off(userid, amount):
    with get_session() as session:
        curren_balance = session.query(Balance).where(Balance.user_id == userid).one_or_none()
        if curren_balance:
            session.query(Balance).where(Balance.user_id == userid).update({'amount': curren_balance.amount - amount})
        else:
            session.save(Balance(userid, -amount))
            session.commit()
