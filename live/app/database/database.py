from sqlmodel import SQLModel, Session, create_engine
from decouple import config

database_connection_string = config("CONNECTION_URI")
url = create_engine(database_connection_string)


def conn():
    SQLModel.metadata.create_all(url)


def session():
    with Session(url) as session:
        yield session
