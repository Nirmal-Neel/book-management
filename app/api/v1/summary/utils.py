from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.books.utils import only_if_book_exists
from core.caching.redis import RedisClient
from core.helpers.db_helper import DbHelper
from core.logger import logger


def datetime_to_string(datetime_obj: datetime) -> str:
    """
    This function converts the datetime object to a specific string format
    """
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")


class SummaryUtils:
    """
    A class that encapsulates all the utility methods required for managing summary
    """

    def __init__(self, db_session: AsyncSession):
        self.db_helper = DbHelper(db_session=db_session)
        self.redis_client = RedisClient()

    @only_if_book_exists
    async def generate_summary_for_book(self, book_id: str):
        """
        This function generates the summary for a book. It is supposed to use Llama3 model
        for summary generation. But that is out of scope. For now, it generates a predefined
        summary. The timestamp in the summary can help to verify that this function was called.
        """
        summary = (f"This is a sample summary generated at {datetime_to_string(datetime.now())}. "
                   f"Actual summary to be generated by Llama3 generative AI model."
                   f" This functionality is not implemented. Thanks!")
        await self.db_helper.store_summary(book_id=book_id, summary=summary)
