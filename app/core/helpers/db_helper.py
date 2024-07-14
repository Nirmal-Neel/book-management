from typing import Sequence, Any

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Book, Review, User
from core.schemas import BookSchema, ReviewSchema


class DbHelper:
    """
    A class that encapsulates all the methods required db operations
    """

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def add_book_row(self, book: dict):
        """
        Inserts a book record and returns the generated id
        """
        query = insert(Book).values(**book).returning(Book)
        result = await self.session.execute(query)
        book = result.scalar_one()
        await self.session.commit()
        return book

    async def get_book(self, filters: dict[str, str]) -> Book | None:
        """
        Fetches a book based on given filters. Returns the book or none
        """
        query = select(Book)
        for key, val in filters.items():
            query = query.where(getattr(Book, key) == val)
        result = await self.session.execute(query)
        book = result.scalar_one_or_none()
        return book

    async def get_all_books(self, page_size: int, current_page: int) -> Sequence[Book]:
        """
        Fetches all the books with pagination
        """
        query = select(Book).offset((current_page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        all_books = result.scalars().all()
        return all_books

    async def update_book_record(self, book_id: str, payload: BookSchema):
        """
        Updates a book record with the provided values
        """
        query = update(Book).where(Book.id == book_id).values(**payload.model_dump(exclude_none=True))
        await self.session.execute(query)
        await self.session.commit()

    async def delete_book_record(self, book_id: str):
        """
        Deletes a book record from DB
        """
        query = delete(Book).where(Book.id == book_id)
        await self.session.execute(query)
        await self.session.commit()

    async def create_review_for_book(self, book_id: str, review: ReviewSchema):
        """
        Creates a review record in DB
        """
        query = insert(Review).values(**{**review.model_dump(), "book_id": book_id})
        await self.session.execute(query)
        await self.session.commit()

    async def get_all_reviews_for_book(self, book_id: str):
        """
        Fetches all reviews for a book
        """
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        book = result.scalar_one_or_none()
        # Since we are using async sqlalchemy, we need to refresh the attributes
        # to load (lazy loading)
        await self.session.refresh(book, ["reviews"])
        if book.reviews:
            for review in book.reviews:
                await self.session.refresh(review, ["user"])
        return book.reviews, book

    async def store_summary(self, book_id: str, summary: str):
        """
        Stores the summary of a book
        """
        query = update(Book).where(Book.id == book_id).values(summary=summary)
        await self.session.execute(query)
        await self.session.commit()

    async def get_user(self, filters: dict[str, Any]) -> User:
        """
        Fetches a user based on provided filters
        """
        query = select(User)
        for key, val in filters.items():
            query = query.where(getattr(User, key) == val)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
