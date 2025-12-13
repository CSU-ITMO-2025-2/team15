from contextlib import contextmanager

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlmodel import SQLModel

database_connection_string = config("CONNECTION_URI")
engine = create_engine(database_connection_string)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def init_db():
  Base.metadata.create_all(bind=engine)


def conn():
  SQLModel.metadata.create_all(engine)


# --- ВАЖНЫЙ МОМЕНТ ---
# Создаем "реестр" сессий.
# Это позволяет получать сессию простым вызовом, без создания новой каждый раз вручную.
db_session = scoped_session(SessionLocal)


def get_session():
  session = SessionLocal()
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()


@contextmanager
def get_session_context():
  session = SessionLocal()
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()
