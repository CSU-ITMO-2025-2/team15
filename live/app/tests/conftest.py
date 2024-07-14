import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import declarative_base
from sqlmodel import SQLModel, Session, create_engine
from database.database import get_session, Base
from sqlalchemy.pool import StaticPool
from auth.authenticate import authenticate
from app import app


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite:///testing.db",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine: Engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, engine: Engine):
    def get_session_override():
        return session

    print("client_fixture")

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[authenticate] = lambda: "test1"

    declarative_base().metadata.create_all(bind=engine)
    SQLModel.metadata.create_all(engine)
    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
