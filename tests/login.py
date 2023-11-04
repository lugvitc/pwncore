from fastapi.testclient import TestClient

from app import app
client = TestClient(app)


def test_login():
    response = client.get("/api/team/login")
    assert response.status_code == 200
    assert response.json() == {"status": "logged in!"}
