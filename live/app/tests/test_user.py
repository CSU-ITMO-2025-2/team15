import uuid

from fastapi.testclient import TestClient

def test_register_new_user(client: TestClient):
    user = {
        "login": "test3",
        "email": "test3-demo-login@test-demo.com",
        "password": "test3"
    }

    response = client.post("/api/user/register", json=user, headers={"Content-Type": "application/json"})
    assert response.status_code == 200 or response.status_code == 409


def test_register_same_user(client: TestClient):
    user = {
        "login": "test3",
        "email": "test3-demo-login@test-demo.com",
        "password": "test3"
    }

    response = client.post("/api/user/register", json=user, headers={"Content-Type": "application/json"})
    assert response.status_code == 409
    assert response.json() == {"detail": "User with email provided exists already."}


def test_signin_with_correct_creds(client: TestClient):
    data = {
        "login": "test3",
        "password": "test3"
    }

    response = client.post("/api/user/signin", json=data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200


def test_signin_with_wrong_creds(client: TestClient):
    data = {
        "login": "test3",
        "password": "test1test1",
    }

    response = client.post("/api/user/signin", json=data, headers={"Content-Type": "application/json"})
    assert response.status_code == 401
