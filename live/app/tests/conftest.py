import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import declarative_base
from sqlmodel import SQLModel, Session, create_engine

from component.user_component import add_client, get_user_by_login
from database.database import get_session, Base
from sqlalchemy.pool import StaticPool
from auth.authenticate import authenticate
from app import app
from ml.const import DATA_ROOT_PATH
from routes.users import hash_password


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

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[authenticate] = lambda: "demo1"

    declarative_base().metadata.create_all(bind=engine)
    SQLModel.metadata.create_all(engine)
    create_fake_data_for_test(session)

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def create_fake_data_for_test(session: Session):
    login = "demo1"
    test_user = get_user_by_login(login, session=session)
    if not test_user:
        add_client(
            login="demo1",
            password=hash_password.create_hash("demo1"),
            email="demo1@demo1.com",
            session=session
        )
