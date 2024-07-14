from base64 import b64encode

import pytest
from starlette import status
from starlette.testclient import TestClient

from core.logger import logger
from main import application


@pytest.fixture(scope="function")
def test_client():
    api_test_client = TestClient(app=application)
    yield api_test_client
    api_test_client.close()


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


def test_generate_summary(test_client):
    # without auth header
    response = test_client.post("http://localhost:8000/api/v1/generate-summary?book_id=test_book")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.post(
        "http://localhost:8000/api/v1/generate-summary?book_id=test_book",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.post(
        "http://localhost:8000/api/v1/generate-summary?book_id=test_book",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # correct one
    payload = {
        "title": "TestGenerateSummary",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2018
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    created_book = response.json()["data"]["book"]

    response = test_client.get(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/summary",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["summary"]["summary"] == ""

    response = test_client.post(
        f"http://localhost:8000/api/v1/generate-summary?book_id={created_book['id']}",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = test_client.get(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/summary",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["summary"]["summary"].startswith("This is a sample summary")

