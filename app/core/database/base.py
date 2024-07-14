from datetime import datetime

from sqlalchemy import TIMESTAMP, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import get_config

config = get_config()


class Base(DeclarativeBase):

    """
    Base class for all the models.
    """

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP")
    )


def get_async_session():
    engine = create_async_engine(
            config.postgres_url.unicode_string(),
            echo=False,
        )
    session = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)
    return session





