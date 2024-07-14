from base64 import b64encode

import pytest
from starlette import status
from starlette.testclient import TestClient

from main import application


@pytest.fixture(scope="function")
def test_client():
    api_test_client = TestClient(app=application)
    yield api_test_client
    api_test_client.close()


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


def test_get_recommendations(test_client):
    # without auth header
    response = test_client.get("http://localhost:8000/api/v1/recommendations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.get(
        "http://localhost:8000/api/v1/recommendations",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # correct one
    response = test_client.get(
        "http://localhost:8000/api/v1/recommendations",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["recommended_books"] == []
