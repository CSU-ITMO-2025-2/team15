from fastapi.testclient import TestClient
from sqlmodel import Session

from component.user_component import get_user_by_login


def test_balance_creation(client: TestClient, session: Session):
    user = get_user_by_login("demo1", session=session)
    print(user)

    response = client.get(f"/api/balance/{user.id}")
    assert response.status_code == 200
    assert response.json()["value"] is not None


def test_balance_refill(client: TestClient, session: Session):
    user = get_user_by_login("demo1", session=session)

    response = client.get(f"/api/balance/{user.id}")
    current_balance = float(response.json()["value"])

    response = client.post(f"/api/balance/replenish/50")
    assert response.status_code == 200
    assert response.json()["message"] == "Balance replenished successfully"

    response = client.get(f"/api/balance/{user.id}")
    new_balance = float(response.json()["value"])
    assert new_balance == (current_balance + 50)
