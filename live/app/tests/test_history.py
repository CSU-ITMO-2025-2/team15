import uuid

from fastapi.testclient import TestClient


def test_get_all_history(client: TestClient):
    res = client.get(url=f"/api/history/all/", headers={"Content-Type": "application/json"})
    assert res.status_code == 200
