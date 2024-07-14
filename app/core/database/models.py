import uuid

from sqlalchemy import String, Integer, ForeignKey, Float, Boolean

from core.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


def generate_uuid():
    return uuid.uuid4().hex


class Book(Base):
    __tablename__ = "books"

    id: Mapped[str] = mapped_column(String, default=generate_uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    genre: Mapped[str] = mapped_column(String, nullable=False)
    year_published: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False, default="")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String, default=generate_uuid, primary_key=True)
    book_id: Mapped[str] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"))
    book: Mapped["Book"] = relationship(backref="reviews")
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship(backref="reviews")
    review_text: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, default=generate_uuid, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    is_privileged: Mapped[bool] = mapped_column(Boolean)
