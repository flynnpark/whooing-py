from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from whooing.exceptions import WhooingAPIError, WhooingAuthError, WhooingRateLimitError
from whooing.types import JsonObject, JsonValue

T = TypeVar("T", bound=JsonValue)


@dataclass(frozen=True, slots=True)
class ApiResponse(Generic[T]):
    code: int | None
    message: str
    rest_of_api: int | None
    error_parameters: JsonObject
    results: T
    raw: JsonObject


def parse_api_response(payload: JsonObject) -> ApiResponse[JsonValue]:
    code = _optional_int(payload.get("code"))
    message = _optional_str(payload.get("message")) or ""
    rest_of_api = _optional_int(payload.get("rest_of_api"))
    error_parameters = _object_or_empty(payload.get("error_parameters"))
    results = payload.get("results", payload)

    if code is not None and code not in {200, 204}:
        error_message = message or f"Whooing API returned code {code}."
        if code in {401, 405}:
            raise WhooingAuthError(
                error_message,
                code=code,
                rest_of_api=rest_of_api,
                error_parameters=error_parameters,
            )
        if code in {402, 429}:
            raise WhooingRateLimitError(
                error_message,
                code=code,
                rest_of_api=rest_of_api,
                error_parameters=error_parameters,
            )
        raise WhooingAPIError(
            error_message,
            code=code,
            rest_of_api=rest_of_api,
            error_parameters=error_parameters,
        )

    return ApiResponse(
        code=code,
        message=message,
        rest_of_api=rest_of_api,
        error_parameters=error_parameters,
        results=results,
        raw=payload,
    )


def _optional_int(value: JsonValue | None) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    return None


def _optional_str(value: JsonValue | None) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _object_or_empty(value: JsonValue | None) -> JsonObject:
    if isinstance(value, dict):
        return value
    return {}
