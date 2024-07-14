from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.json_schema import SkipJsonSchema


class BookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    genre: str = Field(min_length=1)
    year_published: int = Field(gt=1000, le=date.today().year)
    id: SkipJsonSchema[str | None] = None


class ReviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    review_text: str = Field(min_length=1)
    rating: Decimal = Field(ge=0, le=5, decimal_places=1, multiple_of=0.5)
    user_id: SkipJsonSchema[str | None] = None


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str
    id: str


class Meta(BaseModel):
    message: str


class ResponseSchema(BaseModel):
    meta: Meta
    data: dict[str, Any] | None = None
