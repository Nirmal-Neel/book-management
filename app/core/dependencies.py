import secrets
from typing import AsyncGenerator, Annotated

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database.base import get_async_session
from core.exceptions import HTTPException
from core.helpers.db_helper import DbHelper
from core.schemas import UserSchema


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    This function yields the async db session and closes it upon completion
    """
    db = get_async_session()()
    try:
        yield db
    finally:
        await db.close()


async def get_current_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())],
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UserSchema:
    """
    This function returns the current user if credential matches.
    Else, returns error response
    """
    db_helper = DbHelper(db_session)
    provided_username = credentials.username
    provided_password = credentials.password
    user_from_db = await db_helper.get_user(filters={"username": provided_username})
    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect username or password"
        )
    user = UserSchema.model_validate(user_from_db)
    # Uses compare digest from secrets to prevent timing analysis
    is_correct_password = secrets.compare_digest(
        provided_password.encode("utf8"), user.password.encode("utf8")
    )
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Incorrect username or password"
        )
    return user
