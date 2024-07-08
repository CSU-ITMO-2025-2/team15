from database.database import get_session;
from models.model import Transaction


def create_transaction(userid: int, operation_type: str, amount: float):
    with get_session() as session:
        transaction = Transaction(
            userId=userid,
            operationType=operation_type,
            amount=amount
        )
        result = session.add(transaction)
        session.commit()


def get_by_taskid(taskid: int) -> list[Transaction]:
    with get_session() as session:
        return session.query(Transaction).filter(Transaction.taskId == taskid).all()
