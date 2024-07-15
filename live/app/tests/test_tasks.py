import uuid

from fastapi.testclient import TestClient


def test_get_all_tasks(client: TestClient):
    res = client.get(url=f"/api/task/all/", headers={"Content-Type": "application/json"})
    assert res.status_code == 200
