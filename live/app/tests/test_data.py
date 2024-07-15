import uuid

from fastapi.testclient import TestClient


def test_data_upload(client: TestClient):
    data = {
        "fixed_acidity": 0.5,
        "volatile_acidity": 0.5,
        "citric_acid": 0.5,
        "residual_sugar": 0.5,
        "chlorides": 0.5,
        "free_sulfur_dioxide": 0.5,
        "total_sulfur_dioxide": 0.5,
        "density": 0.5,
        "pH": 0.5,
        "sulphates": 0.5,
        "alcohol": 0.5
    }

    response = client.post("/api/df/upload", json=data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200 or response.status_code == 409


def test_get_all_data(client: TestClient):
    response = client.get("/api/df/all/", headers={"Content-Type": "application/json"})
    assert response.status_code == 200
