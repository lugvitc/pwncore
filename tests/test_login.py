from fastapi.testclient import TestClient

from app import app
client = TestClient(app)


def test_login():
    # Send a GET response to the specified endpoint
    response = client.get("/api/team/login")

    # Evaluate the response against expected values
    assert response.status_code == 200
    assert response.json() == {"status": "logged in!"}
