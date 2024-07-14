from typing import Annotated

from fastapi import Depends, Query, Path
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from pydantic import AfterValidator
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.books.utils import BookUtils
from core.dependencies import get_db_session, get_current_user
from core.responses import generate_json_response
from core.schemas import BookSchema, ReviewSchema, UserSchema

book_route = APIRouter(prefix="/books")


@book_route.post("")
async def create_a_book(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    payload: BookSchema
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    created_book = await book_utils.store_book_to_db(book=payload)
    return generate_json_response(
        status_code=status.HTTP_201_CREATED,
        message="Book is created",
        data={"book": created_book}
    )


@book_route.get("")
async def get_all_books(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    current_page: Annotated[int, Query(alias="currentPage", gt=0)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", gt=0)] = 25
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    all_books = await book_utils.retrieve_all_books(page_size=page_size, current_page=current_page)
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Books are fetched",
        data={"books": all_books}
    )


@book_route.get("/{book_id}")
async def get_book_by_id(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Path(min_length=1)]
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    book = await book_utils.retrieve_a_book(book_id=book_id)
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Book is fetched",
        data={"book": book}
    )


@book_route.put("/{book_id}")
async def update_book_by_id(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Path(min_length=1)],
    payload: BookSchema
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    await book_utils.update_book(book_id=book_id, payload=payload)
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Updated successfully"
    )


@book_route.delete("/{book_id}")
async def delete_book_by_id(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Path(min_length=1)]
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    await book_utils.delete_book(book_id=book_id)
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Deleted successfully"
    )


@book_route.post("/{book_id}/reviews")
async def add_a_review(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Path(min_length=1)],
    payload: ReviewSchema
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    payload.user_id = current_user.id
    await book_utils.store_a_review(book_id=book_id, payload=payload)
    return generate_json_response(
        status_code=status.HTTP_201_CREATED,
        message="Review is added"
    )


@book_route.get("/{book_id}/reviews")
async def get_all_reviews(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Path(min_length=1)]
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    reviews = await book_utils.retrieve_all_reviews(book_id=book_id)
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Reviews are fetched",
        data={"reviews": reviews}
    )


@book_route.get("/{book_id}/summary")
async def get_summary_and_rating(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    _: Annotated[UserSchema, Depends(get_current_user)],
    book_id: Annotated[str, AfterValidator(lambda x: x.strip()), Path(min_length=1)]
) -> JSONResponse:
    book_utils = BookUtils(db_session=db_session)
    summary_and_ratings = await book_utils.retrieve_summary_and_rating(book_id=book_id)
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Summary and ratings are fetched",
        data={"summary": summary_and_ratings}
    )
