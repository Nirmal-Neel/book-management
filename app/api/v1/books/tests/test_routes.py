from base64 import b64encode

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from starlette import status

from main import application


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


@pytest.fixture(scope="function")
def test_client():
    api_test_client = TestClient(app=application)
    yield api_test_client
    api_test_client.close()


def test_create_a_book(test_client):
    # without auth header
    response = test_client.post("http://localhost:8000/api/v1/books")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # with incorrect payload
    # without title
    payload = {
      "author": "TestAuthor",
      "genre": "TestGenre",
      "year_published": 2024
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == "Missing title in body"

    # without author
    payload = {
        "title": "TestTitle",
        "genre": "TestGenre",
        "year_published": 2024
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == "Missing author in body"

    # without genre
    payload = {
        "title": "TestTitle",
        "author": "TestAuthor",
        "year_published": 2024
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == "Missing genre in body"

    # without year_published
    payload = {
        "title": "TestTitle",
        "author": "TestAuthor",
        "genre": "TestGenre"
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == "Missing year_published in body"

    # with invalid year_published
    payload = {
        "title": "TestTitle",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2028
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for year_published in body. "
                                                  "Input should be less than or equal to 2024")

    payload = {
        "title": "TestTitle",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 1000
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for year_published in body. "
                                                  "Input should be greater than 1000")

    # with invalid title
    payload = {
        "title": " ",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2028
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for title in body. "
                                                  "String should have at least 1 character")

    # with invalid author
    payload = {
        "title": "TestTile",
        "author": "  ",
        "genre": "TestGenre",
        "year_published": 2028
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for author in body. "
                                                  "String should have at least 1 character")

    # with invalid genre
    payload = {
        "title": "TestTile",
        "author": "TestAuthor",
        "genre": "  ",
        "year_published": 2028
    }
    response = test_client.post(
        "http://localhost:8000/api/v1/books",
        json=payload,
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for genre in body. "
                                                  "String should have at least 1 character")

    # correct one
    payload = {
        "title": "TestTitle",
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
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["meta"]["message"] == "Book is created"
    assert response.json()["data"]["book"]["title"] == "TestTitle"
    assert "id" in response.json()["data"]["book"]


def test_get_all_books(test_client):
    # without auth header
    response = test_client.get("http://localhost:8000/api/v1/books")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.get(
        "http://localhost:8000/api/v1/books",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # with invalid page_size
    response = test_client.get(
        "http://localhost:8000/api/v1/books?pageSize=0",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for pageSize in query. "
                                                  "Input should be greater than 0")

    # with invalid current_page
    response = test_client.get(
        "http://localhost:8000/api/v1/books?currentPage=-1",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for currentPage in query. "
                                                  "Input should be greater than 0")

    # correct one
    response = test_client.get(
        "http://localhost:8000/api/v1/books",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json()["data"]["books"], list) is True


def test_get_book_by_id(test_client):
    # without auth header
    response = test_client.get("http://localhost:8000/api/v1/books/test_book_id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.get(
        "http://localhost:8000/api/v1/books/test_book_id",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.get(
        "http://localhost:8000/api/v1/books/test_book",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # invalid book
    response = test_client.get(
        "http://localhost:8000/api/v1/books/   ",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == "Invalid value for book_id in path"

    # correct one
    payload = {
        "title": "TestGetBookById",
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
        f"http://localhost:8000/api/v1/books/{created_book['id']}",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["book"] == created_book


def test_update_book_by_id(test_client):
    # without auth header
    response = test_client.put("http://localhost:8000/api/v1/books/test_book_id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.put(
        "http://localhost:8000/api/v1/books/test_book_id",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.put(
        "http://localhost:8000/api/v1/books/test_book",
        json={
            "title": "TestUpdateBookById",
            "author": "TestAuthor",
            "genre": "TestGenre",
            "year_published": 2018
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # correct one
    payload = {
        "title": "TestUpdateBookById",
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

    test_client.put(
        f"http://localhost:8000/api/v1/books/{created_book['id']}",
        json={
            **payload,
            "year_published": 2020
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )

    response = test_client.get(
        f"http://localhost:8000/api/v1/books/{created_book['id']}",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["book"]["year_published"] == 2020


def test_delete_book_by_id(test_client):
    # without auth header
    response = test_client.delete("http://localhost:8000/api/v1/books/test_book_id")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.delete(
        "http://localhost:8000/api/v1/books/test_book_id",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.delete(
        "http://localhost:8000/api/v1/books/test_book",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # correct one
    payload = {
        "title": "TestDeleteBookById",
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

    response = test_client.delete(
        f"http://localhost:8000/api/v1/books/{created_book['id']}",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    response = test_client.get(
        "http://localhost:8000/api/v1/books/{created_book['id']}",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"


def test_add_a_review(test_client):
    # without auth header
    response = test_client.post("http://localhost:8000/api/v1/books/test_book_id/reviews")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.post(
        "http://localhost:8000/api/v1/books/test_book_id/reviews",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.post(
        "http://localhost:8000/api/v1/books/test_book/reviews",
        json={
            "review_text": "TestReview",
            "rating": 1
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # with invalid review_text
    response = test_client.post(
        "http://localhost:8000/api/v1/books/test_book/reviews",
        json={
            "review_text": "  ",
            "rating": 1
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for review_text in body. "
                                                  "String should have at least 1 character")

    # with invalid rating
    response = test_client.post(
        "http://localhost:8000/api/v1/books/test_book/reviews",
        json={
            "review_text": "TestReview",
            "rating": 10
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for rating in body. "
                                                  "Input should be less than or equal to 5")

    response = test_client.post(
        "http://localhost:8000/api/v1/books/test_book/reviews",
        json={
            "review_text": "TestReview",
            "rating": -2
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for rating in body. "
                                                  "Input should be greater than or equal to 0")

    response = test_client.post(
        "http://localhost:8000/api/v1/books/test_book/reviews",
        json={
            "review_text": "TestReview",
            "rating": 2.3
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["meta"]["message"] == ("Invalid value for rating in body. "
                                                  "Input should be a multiple of 0.5")

    # correct one
    payload = {
        "title": "TestAddAReview",
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

    response = test_client.post(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/reviews",
        json={
            "review_text": "TestReview",
            "rating": 3.5
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_get_all_reviews(test_client):
    # without auth header
    response = test_client.get("http://localhost:8000/api/v1/books/test_book_id/reviews")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.get(
        "http://localhost:8000/api/v1/books/test_book_id/reviews",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.get(
        "http://localhost:8000/api/v1/books/test_book/reviews",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # correct one
    payload = {
        "title": "TestGetAllReviews",
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
    test_client.post(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/reviews",
        json={
            "review_text": "TestReview",
            "rating": 3.5
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )

    response = test_client.get(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/reviews",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["reviews"][0] == {
            "review_text": "TestReview",
            "user": "user"
        }


def test_get_summary_and_rating(test_client):
    # without auth header
    response = test_client.get("http://localhost:8000/api/v1/books/test_book_id/summary")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Not authenticated"

    # with incorrect credentials
    response = test_client.get(
        "http://localhost:8000/api/v1/books/test_book_id/summary",
        headers={
            "Authorization": basic_auth("user", "pass")
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["meta"]["message"] == "Incorrect username or password"

    # non existing book
    response = test_client.get(
        "http://localhost:8000/api/v1/books/test_book/summary",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["meta"]["message"] == "Book not found"

    # correct one
    payload = {
        "title": "TestGetSummaryAndRating",
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
    test_client.post(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/reviews",
        json={
            "review_text": "TestReview",
            "rating": 3.5
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    test_client.post(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/reviews",
        json={
            "review_text": "TestReview",
            "rating": 3
        },
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )

    response = test_client.get(
        f"http://localhost:8000/api/v1/books/{created_book['id']}/summary",
        headers={
            "Authorization": basic_auth("user", "user123")
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["summary"]["rating"] == 3.2
    assert response.json()["data"]["summary"]["summary"] == ""

