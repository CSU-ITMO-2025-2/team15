from sqlalchemy import Column, String, Integer, Date, ForeignKey, Float, LargeBinary
from database.database import Base, engine
from datetime import datetime as dtime


class User(Base):
    __tablename__ = "susers"
    id = Column(Integer, primary_key=True, nullable=False)
    login = Column(String)
    email = Column(String)
    role = Column(String)

    def __init__(self, login, email, role):
        super().__init__()
        self.login = login
        self.email = email
        self.role = role

    def __str__(self) -> str:
        return self.login


class Balance(Base):
    __tablename__ = "balances"
    id = Column(Integer, primary_key=True, nullable=False)
    userId = Column(Integer, ForeignKey("susers.id"))
    value = Column(Float)

    def __init__(self, userId, value):
        super().__init__()
        self.userId = userId
        self.value = value


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, nullable=False)
    userId = Column(Integer, ForeignKey("susers.id"))
    operationType = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    datetime = Column(Date, nullable=False)

    def __init__(
        self,
        userId,
        operationType,
        amount,
        datetime=dtime.now(),
    ):
        super().__init__()
        self.userId = userId
        self.operationType = operationType
        self.amount = amount
        self.datetime = datetime


class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, nullable=False)
    data = Column(LargeBinary, nullable=False)
    data_params = Column(String, nullable=False)

    def __init__(self, data, data_params):
        self.data = data
        self.data_params = data_params


class Model(Base):
    __tablename__ = "model"
    id = Column(Integer, primary_key=True, nullable=False)
    path2model = Column(String, nullable=False)

    def __init__(self, path2model):
        self.path2model = path2model


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, nullable=False)
    task_type = Column(String, nullable=False)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    userid = Column(Integer, ForeignKey("susers.id"), nullable=False)
    dataid = Column(Integer, ForeignKey("data.id"), nullable=False)
    modelid = Column(Integer, ForeignKey("model.id"), nullable=False)
    processing_start = Column(Date, nullable=False)
    processing_end = Column(Date)
    status = Column(String, nullable=False)

    def __init__(
        self,
        task_type,
        transaction_id,
        userid,
        dataid,
        processing_start,
        processing_end,
        status
    ):
        super().__init__()
        self.task_type = task_type,
        self.transaction_id = transaction_id
        self.userid = userid
        self.dataid = dataid
        self.processing_start = processing_start
        self.processing_end = processing_end
        self.status = status


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, nullable=False)
    userid = Column(Integer, ForeignKey("susers.id"), nullable=False)
    taskid = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    operation_type = Column(String, nullable=False)
    datetime = Column(Date, nullable=False)
    details = Column(String, nullable=True)

    def __init__(
            self,
            userid,
            taskid,
            operation_type,
            datetime=dtime.now(),
            details=""
    ):
            super().__init__()
            self.userid
            self.userid = userid
            self.taskid = taskid
            self.operation_type = operation_type
            self.datetime = datetime
            self.details = details


class Notification(Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, nullable=False)
    userId = Column(Integer, ForeignKey("susers.id"))
    message = Column(String, nullable=False)
    processed = Column(Integer, nullable=False)

    def __init__(self, userId, message, processed=0):
        super().__init__()
        self.userId = userId
        self.message = message
        self.processed = processed


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
