from __future__ import annotations

from enum import IntEnum
from typing import Generic, Literal, TypeAlias, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

T = TypeVar("T")


class WhooingModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApiCode(IntEnum):
    OK = 200
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    API_LIMIT_EXCEEDED = 402
    AUTH_EXPIRED = 405
    INTERNAL_ERROR = 500


class ErrorParameters(WhooingModel):
    field: str | None = None
    parameter: str | None = None
    reason: str | None = None
    expected: str | int | float | bool | None = None
    actual: str | int | float | bool | None = None


def _normalize_error_parameters(value: object) -> object:
    if value is None:
        return {}
    if isinstance(value, list) and len(value) == 0:
        return {}
    return value


class WhooingResponseMetadata(WhooingModel):
    message: str = ""
    error_parameters: ErrorParameters = Field(default_factory=ErrorParameters)
    rest_of_api: int | None = None

    @field_validator("error_parameters", mode="before")
    @classmethod
    def normalize_error_parameters(cls, value: object) -> object:
        return _normalize_error_parameters(value)


class WhooingEnvelope(WhooingResponseMetadata):
    code: ApiCode | int | None = None


class WhooingAPIResponse(WhooingResponseMetadata, Generic[T]):
    code: ApiCode | int | None = None
    results: T | None = None


class WhooingSuccessResponse(WhooingResponseMetadata, Generic[T]):
    code: Literal[ApiCode.OK, 200] = ApiCode.OK
    results: T


class WhooingNoContentResponse(WhooingResponseMetadata):
    code: Literal[ApiCode.NO_CONTENT, 204] = ApiCode.NO_CONTENT
    results: None = None

    @model_validator(mode="after")
    def validate_no_content_message(self) -> WhooingNoContentResponse:
        if self.message and self.message.lower() not in {"", "no content"}:
            return self
        return self


class WhooingErrorResponse(WhooingResponseMetadata):
    code: Literal[
        ApiCode.BAD_REQUEST,
        ApiCode.UNAUTHORIZED,
        ApiCode.API_LIMIT_EXCEEDED,
        ApiCode.AUTH_EXPIRED,
        ApiCode.INTERNAL_ERROR,
        400,
        401,
        402,
        405,
        500,
    ]
    results: None = None


class HttpRateLimitResponse(WhooingModel):
    status_code: Literal[429] = 429
    retry_after: float | None = None


WhooingStrictResponse: TypeAlias = (
    WhooingSuccessResponse[T] | WhooingNoContentResponse | WhooingErrorResponse
)
