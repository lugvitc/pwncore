from fastapi.testclient import TestClient

from pwncore import app

client = TestClient(app)


# Example test
def test_login():
    # Send a GET response to the specified endpoint
    response = client.get("/api/team/login")

    # Evaluate the response against expected values
    assert response.status_code == 404
