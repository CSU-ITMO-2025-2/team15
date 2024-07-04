
from live.app.models.model import Notification
from live.app.database.database import session


def add_notififcation(userid: int, message):
    with session() as session:
        session.begin()
        session.save(Notification(userId=userid, message=message))
        session.commit()


def get_not_processed_notifications():
    with session() as session:
        return session.query(Notification).where(Notification.processed == 0)


def final_notifications(notificationIds: list):
    with session() as session:
        session.query(Notification).filter(Notification in notificationIds).update({'processed': 1})
        session.commit()

