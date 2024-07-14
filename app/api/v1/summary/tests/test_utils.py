import asyncio
import datetime

import pytest
import pytest_asyncio
from sqlalchemy import delete, insert, select

from api.v1.summary.utils import SummaryUtils, datetime_to_string
from core.database.base import get_async_session
from core.database.models import Book
from core.exceptions import HTTPException


@pytest_asyncio.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    session_object = get_async_session()()
    yield session_object
    await session_object.execute(
        delete(Book)
    )
    await session_object.commit()
    await session_object.close()


@pytest.mark.asyncio
async def test_generate_summary_for_book(db_session):
    summary_utils = SummaryUtils(db_session)
    with pytest.raises(HTTPException) as he:
        await summary_utils.generate_summary_for_book(book_id="non-existing-book")
    assert he.value.message == "Book not found"

    book_payload = {
        "title": "TestBook",
        "author": "TestAuthor",
        "genre": "TestGenre",
        "year_published": 2024
    }

    result = await db_session.execute(
        insert(Book).values(**book_payload).returning(Book.id)
    )
    book_id = result.scalar_one()
    await summary_utils.generate_summary_for_book(book_id=book_id)

    result = await db_session.execute(
        select(Book).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    assert book.summary.startswith("This is a sample summary")


async def test_datetime_to_string():
    datetime_obj = datetime.datetime.strptime("2024-07-13 15:32:00", "%Y-%m-%d %H:%M:%S")
    datetime_str = datetime_to_string(datetime_obj)
    assert datetime_str == "2024-07-13 15:32:00"
