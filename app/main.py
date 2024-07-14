from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from starlette import status
from starlette.responses import JSONResponse
from starlette.requests import Request

from api.v1.routes import v1_router
from core.exceptions import HTTPException
from core.responses import generate_json_response

application = FastAPI(debug=True)


application.include_router(v1_router)


@application.exception_handler(HTTPException)
async def return_error_response(_: Request, exc: HTTPException) -> JSONResponse:
    """
    It handles HTTPException
    """
    return generate_json_response(message=exc.message, status_code=exc.status_code)


@application.exception_handler(FastAPIHTTPException)
async def return_error_response(_: Request, exc: HTTPException) -> JSONResponse:
    """
    It handles HTTPException
    """
    return generate_json_response(message=exc.detail, status_code=exc.status_code)


@application.exception_handler(RequestValidationError)
async def return_validation_error_message(_: Request, exc: RequestValidationError) -> JSONResponse:
    """
    It handles RequestValidationError. Based on error type, it generates meaningful messages.
    """
    error = exc.errors()[0]
    if error["type"] == "missing":
        message = f"Missing {error['loc'][-1]}"
        if error["loc"][-1] != "body":
            message += f" in {error['loc'][0]}"
    elif error["type"] == "json_invalid":
        message = "Invalid request body"
    elif error["type"] == "invalid_data":
        message = error["msg"]
    elif error["type"] in [
        "greater_than",
        "string_too_short",
        "greater_than_equal",
        "less_than_equal",
        "multiple_of",
        "decimal_max_places"
    ]:
        message = f"Invalid value for {error['loc'][-1]} in {error['loc'][0]}. {error['msg']}"
    else:
        message = f"Invalid value for {error['loc'][-1]} in {error['loc'][0]}"
    return generate_json_response(
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST
    )
