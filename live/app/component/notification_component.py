
from models.model import Notification
from database.database import get_session


def add_notififcation(userid: int, message):
    with get_session() as session:
        session.begin()
        session.add(Notification(userId=userid, message=message))
        session.commit()


def get_not_processed_notifications():
    with get_session() as session:
        return session.query(Notification).where(Notification.processed == 0)


def final_notifications(notificationIds: list):
    with get_session() as session:
        session.query(Notification).filter(Notification in notificationIds).update({'processed': 1})
        session.commit()

