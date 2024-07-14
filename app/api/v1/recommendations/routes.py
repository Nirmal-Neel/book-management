from typing import Annotated

from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from starlette import status

from core.dependencies import get_current_user
from core.responses import generate_json_response
from core.schemas import UserSchema

recommendation_route = APIRouter(prefix="")


@recommendation_route.get("/recommendations")
async def get_recommendations(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
) -> JSONResponse:
    # NOT IMPLEMENTED
    return generate_json_response(
        status_code=status.HTTP_200_OK,
        message="Recommendations are fetched",
        data={"recommended_books": []}
    )
