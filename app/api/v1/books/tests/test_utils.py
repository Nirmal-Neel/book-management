import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import insert, select, delete, update

from api.v1.books.utils import BookUtils
from core.database.base import get_async_session
from core.database.models import Book, User, Review
from core.exceptions import HTTPException
from core.schemas import BookSchema, ReviewSchema


@pytest_asyncio.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="function")
async def db_session():
    session_object = get_async_session()()
    yield session_object
    await session_object.execute(
        delete(Book)
    )
    await session_object.execute(
        delete(Review)
    )
    await session_object.commit()
    await session_object.close()


async def test_store_book_to_db(db_session):
    book_payload = {
            "title": "TestBookStore",
            "author": "TestAuthor",
            "genre": "TestGenre",
            "year_published": 2024
        }
    book_utils = BookUtils(db_session)
    await book_utils.store_book_to_db(BookSchema(**book_payload))
    result = await db_session.execute(
        select(Book).where(Book.title == book_payload['title'])
    )
    book = result.scalar_one_or_none()
    assert book.author == book_payload['author']
    assert book.year_published == book_payload['year_published']

    with pytest.raises(HTTPException) as he:
        await book_utils.store_book_to_db(BookSchema(**book_payload))
    assert he.value.message == f"A book with {book_payload['title']} of author {book_payload['author']} already exists"


async def test_retrieve_all_books(db_session):
    book_payload = {
        "title": "TestBookRetrieve",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    book_utils = BookUtils(db_session)
    all_books = await book_utils.retrieve_all_books(page_size=5, current_page=1)
    assert len(all_books) == 0

    await db_session.execute(
        insert(Book).values(**book_payload)
    )
    await db_session.commit()

    all_books = await book_utils.retrieve_all_books(page_size=5, current_page=1)
    assert len(all_books) == 1
    assert all_books[0]['title'] == "TestBookRetrieve"
    assert all_books[0]['author'] == "TestAuthor"

    all_books = await book_utils.retrieve_all_books(page_size=5, current_page=2)
    assert len(all_books) == 0


async def test_retrieve_a_book(db_session):
    book_payload = {
        "title": "TestBookRetrieveABook",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()
    await db_session.commit()
    book_utils = BookUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await book_utils.retrieve_a_book(book_id="non-existing-book-id")
    assert he.value.message == "Book not found"
    book = await book_utils.retrieve_a_book(book_id=book_id)
    assert book is not None
    assert book['title'] == "TestBookRetrieveABook"
    assert book['author'] == "TestAuthor"
    assert book['id'] == book_id


async def test_update_book(db_session):
    book_payload = {
        "title": "TestBookUpdateBook",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    book_utils = BookUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await book_utils.update_book(book_id="non-existing-id", payload=BookSchema(**book_payload))
    assert he.value.message == "Book not found"

    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()
    update_payload = {
        **book_payload,
        "title": "NewBookUpdateBook"
    }
    await book_utils.update_book(book_id=book_id, payload=BookSchema(**update_payload))
    result = await db_session.execute(
        select(Book).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    assert book is not None
    assert book.title == "NewBookUpdateBook"


async def test_delete_book(db_session):
    book_payload = {
        "title": "TestBookDeleteBook",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    book_utils = BookUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await book_utils.delete_book(book_id="non-existing-id")
    assert he.value.message == "Book not found"

    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()
    await book_utils.delete_book(book_id=book_id)
    result = await db_session.execute(
        select(Book).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    assert book is None


async def test_store_a_review(db_session):
    book_payload = {
        "title": "TestBookStoreAReview",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    result = await db_session.execute(
        select(User.id).where(User.username == "user")
    )
    user_id = result.scalar_one()

    review_payload = {
        "review_text": "TestReview",
        "rating": 5,
        "user_id": user_id
    }
    book_utils = BookUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await book_utils.store_a_review(book_id="non-existing-id", payload=ReviewSchema(**review_payload))
    assert he.value.message == "Book not found"

    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()

    result = await db_session.execute(
        select(Review).where(Review.book_id == book_id)
    )
    review = result.scalar_one_or_none()
    assert review is None

    await book_utils.store_a_review(book_id=book_id, payload=ReviewSchema(**review_payload))
    result = await db_session.execute(
        select(Review).where(Review.book_id == book_id)
    )
    review = result.scalar_one_or_none()
    assert review is not None
    assert review.review_text == "TestReview"
    assert review.rating == 5
    assert review.user_id == user_id


async def test_retrieve_all_reviews(db_session):
    result = await db_session.execute(
        select(User.id).where(User.username == "user")
    )
    user_id = result.scalar_one()

    book_utils = BookUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await book_utils.retrieve_all_reviews(book_id="non-existing-id")
    assert he.value.message == "Book not found"

    book_payload = {
        "title": "TestBookRetrieveAllReviews",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()

    all_reviews = await book_utils.retrieve_all_reviews(book_id=book_id)
    assert len(all_reviews) == 0

    review_payload_1 = {
        "review_text": "TestReview 1",
        "rating": 5,
        "user_id": user_id
    }
    review_payload_2 = {
        "review_text": "TestReview 2",
        "rating": 3,
        "user_id": user_id
    }

    await book_utils.store_a_review(book_id=book_id, payload=ReviewSchema(**review_payload_1))
    await book_utils.store_a_review(book_id=book_id, payload=ReviewSchema(**review_payload_2))

    all_reviews = await book_utils.retrieve_all_reviews(book_id=book_id)
    assert len(all_reviews) == 2
    for review in all_reviews:
        assert review["user"] == "user"


async def test_retrieve_summary_and_rating(db_session):
    result = await db_session.execute(
        select(User.id).where(User.username == "user")
    )
    user_id = result.scalar_one()

    book_utils = BookUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await book_utils.retrieve_summary_and_rating(book_id="non-existing-id")
    assert he.value.message == "Book not found"

    book_payload = {
        "title": "TestBookSummaryAndRating",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }
    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()

    summary_and_rating = await book_utils.retrieve_summary_and_rating(book_id=book_id)
    assert summary_and_rating['rating'] == 0
    assert summary_and_rating['summary'] == ""

    review_payload_1 = {
        "review_text": "TestReview 1",
        "rating": 4,
        "user_id": user_id,
        "book_id": book_id
    }
    review_payload_2 = {
        "review_text": "TestReview 2",
        "rating": 3,
        "user_id": user_id,
        "book_id": book_id
    }
    await db_session.execute(
        insert(Review).values(**review_payload_1)
    )
    await db_session.execute(
        insert(Review).values(**review_payload_2)
    )
    await db_session.execute(
        update(Book).where(Book.id == book_id).values(summary="TestSummary")
    )
    await db_session.commit()

    summary_and_rating = await book_utils.retrieve_summary_and_rating(book_id=book_id)
    assert summary_and_rating['rating'] == 3.5
    assert summary_and_rating['summary'] == "TestSummary"


