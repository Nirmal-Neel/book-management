from typing import Any
from fastapi.responses import JSONResponse

from core.schemas import ResponseSchema, Meta


def generate_json_response(
    message: str,
    status_code: int,
    data: dict[str, Any] | None = None
) -> JSONResponse:
    meta = Meta(message=message)
    response = ResponseSchema(meta=meta, data=data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=status_code)
