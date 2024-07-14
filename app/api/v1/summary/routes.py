from typing import Annotated

from fastapi import Depends, Query
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from pydantic import AfterValidator
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.summary.utils import SummaryUtils
from core.dependencies import get_db_session, get_current_user
from core.responses import generate_json_response
from core.schemas import UserSchema

summary_route = APIRouter(prefix="")


@summary_route.post("/generate-summary")
async def generate_summary(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Query(..., min_length=1)]
) -> JSONResponse:
    summary_utils = SummaryUtils(db_session)
    await summary_utils.generate_summary_for_book(book_id=book_id)
    return generate_json_response(
        status_code=status.HTTP_201_CREATED,
        message="Summary is generated"
    )
