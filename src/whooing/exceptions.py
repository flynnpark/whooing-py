from __future__ import annotations

from collections.abc import Mapping

from whooing.types import JsonValue


class WhooingError(Exception):
    """Base exception for errors raised by this package."""


class WhooingTransportError(WhooingError):
    """Raised when the HTTP transport fails before a Whooing response is available."""


class WhooingResponseError(WhooingError):
    def __init__(self, message: str, *, status_code: int, body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class WhooingPydanticError(WhooingError):
    """Raised when optional Pydantic response parsing cannot be completed."""


class WhooingPydanticUnavailableError(WhooingPydanticError):
    """Raised when Pydantic helpers are used without installing the optional extra."""


class WhooingAPIError(WhooingError):
    def __init__(
        self,
        message: str,
        *,
        code: int,
        rest_of_api: int | None,
        error_parameters: Mapping[str, JsonValue],
        http_status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.rest_of_api = rest_of_api
        self.error_parameters = dict(error_parameters)
        self.http_status_code = http_status_code


class WhooingAuthError(WhooingAPIError):
    """Raised for authentication and authorization failures."""


class WhooingOAuthError(WhooingError):
    def __init__(self, error: str, description: str | None = None) -> None:
        message = error if description is None else f"{error}: {description}"
        super().__init__(message)
        self.error = error
        self.description = description


class WhooingRateLimitError(WhooingAPIError):
    """Raised when the API quota or short-term request limit is exceeded."""

    def __init__(
        self,
        message: str,
        *,
        code: int,
        rest_of_api: int | None,
        error_parameters: Mapping[str, JsonValue],
        http_status_code: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(
            message,
            code=code,
            rest_of_api=rest_of_api,
            error_parameters=error_parameters,
            http_status_code=http_status_code,
        )
        self.retry_after = retry_after
