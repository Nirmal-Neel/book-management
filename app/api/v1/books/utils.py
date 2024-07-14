import functools
import json

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.caching.redis import RedisClient
from core.exceptions import HTTPException
from core.helpers.db_helper import DbHelper
from core.logger import logger
from core.schemas import BookSchema, ReviewSchema


def only_if_book_exists(func):
    """
    Decorator that checks if the book exists or not.
    First it checks in the cache. If not available, then goes to DB
    """
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        """
        First it checks in the cache. If not found then in DB. If not found, then exception
        """
        redis_client = RedisClient()
        book = await redis_client.get_cache(key=f"book:{kwargs.get('book_id')}")
        if not book:
            book = await self.db_helper.get_book(filters={"id": kwargs.get("book_id")})
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message="Book not found")
        return await func(self, *args, **kwargs)
    return wrapped


class BookUtils:
    """
    A class that encapsulates all the utility methods required for managing book
    """

    def __init__(self, db_session: AsyncSession):
        self.db_helper = DbHelper(db_session=db_session)
        self.redis_client = RedisClient()

    async def store_book_to_db(self, book: BookSchema):
        """
        This method takes the book payload and stores to DB. Also writes to cache.
        """
        existing_book = await self.db_helper.get_book(filters={"title": book.title, "author": book.author})
        if existing_book:
            # If a book already exists with same name and author, then it returns error response
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                message=f"A book with {book.title} of author {book.author} already exists"
            )
        inserted_book = await self.db_helper.add_book_row(book.model_dump(exclude_none=True))
        await self.redis_client.set_cache(key=f"book:{inserted_book.id}", value=book.model_dump_json())
        return BookSchema.model_validate(inserted_book).model_dump()

    async def retrieve_all_books(self, page_size: int, current_page: int):
        """
        This method retrieves all books from DB using pagination and returns to the user.
        Currently, this method returns only the id, title and the author name. If needed,
        it can be updated..
        """
        all_books_model = await self.db_helper.get_all_books(page_size=page_size, current_page=current_page)
        all_books = [
            {**BookSchema.model_validate(book).model_dump(include={"author", "title", "id"})}
            for book in all_books_model
        ]
        return all_books

    async def retrieve_a_book(self, book_id: str):
        """
        This method returns the complete details of a book
        """
        # It will first check in cache. If not available, then it fetches from DB
        book = await self.redis_client.get_cache(key=f"book:{book_id}")
        if book:
            book = json.loads(book)
            return book
        else:
            book = await self.db_helper.get_book(filters={"id": book_id})
            # if book does not exist, it returns an error response
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, message="Book not found")
            book_dict = BookSchema.model_validate(book).model_dump()
            # updates the cache with the book content
            await self.redis_client.set_cache(key=f"book:{book_id}", value=json.dumps(book_dict))
            return book_dict

    @only_if_book_exists
    async def update_book(self, book_id: str, payload: BookSchema):
        """
        This method updates the book based on user request
        """
        # First it updates in DB
        await self.db_helper.update_book_record(book_id=book_id, payload=payload)
        # then it updates the cache
        await self.redis_client.set_cache(key=f"book:{book_id}", value=payload.model_dump_json())

    @only_if_book_exists
    async def delete_book(self, book_id: str):
        """
        This method deletes a book
        """
        # First it deletes from DB
        await self.db_helper.delete_book_record(book_id=book_id)
        # then it deletes from cache
        await self.redis_client.unset_cache(key=f"book:{book_id}")

    @only_if_book_exists
    async def store_a_review(self, book_id: str, payload: ReviewSchema):
        """
        This method stores a review for a book
        """
        await self.db_helper.create_review_for_book(book_id=book_id, review=payload)

    @only_if_book_exists
    async def retrieve_all_reviews(self, book_id: str):
        """
        This method prepares all the reviews for a book. Review text and the username
        of the user who wrote the review is returned
        """
        # First it fetches all the reviews from DB
        review_models, _ = await self.db_helper.get_all_reviews_for_book(book_id=book_id)
        # Then it filters the fields
        reviews = [
            {
                "review_text": review.review_text,
                "user": review.user.username
            }
            for review in review_models
        ]
        return reviews

    @only_if_book_exists
    async def retrieve_summary_and_rating(self, book_id: str):
        """
        This method prepares the summary and the average rating of a book
        """
        # First it fetches the book object and all the reviews for the book
        review_models, book = await self.db_helper.get_all_reviews_for_book(book_id=book_id)
        # Then it prepares a list of ratings
        ratings = [
            review.rating for review in review_models
        ]
        # Then it calculates the average rating
        rating = round(sum(ratings)/max(len(ratings), 1), 1)
        summary = book.summary
        # returns the summary and the average rating
        return {
            "summary": summary,
            "rating": rating
        }
