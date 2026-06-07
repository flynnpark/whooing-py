"""Typed Python client library for the Whooing Developer API."""

from whooing.async_client import AsyncWhooingClient
from whooing.auth import (
    APIKeyAuth,
    AsyncOAuth2TokenClient,
    BearerTokenAuth,
    OAuth1aAuth,
    OAuth2Token,
    OAuth2TokenClient,
)
from whooing.client import WhooingClient
from whooing.exceptions import (
    WhooingAPIError,
    WhooingAuthError,
    WhooingError,
    WhooingOAuthError,
    WhooingPydanticError,
    WhooingPydanticUnavailableError,
    WhooingRateLimitError,
    WhooingResponseError,
    WhooingTransportError,
)
from whooing.response import ApiResponse

__version__ = "0.1.0"

__all__ = [
    "APIKeyAuth",
    "ApiResponse",
    "AsyncWhooingClient",
    "AsyncOAuth2TokenClient",
    "BearerTokenAuth",
    "OAuth1aAuth",
    "OAuth2Token",
    "OAuth2TokenClient",
    "WhooingAPIError",
    "WhooingAuthError",
    "WhooingClient",
    "WhooingError",
    "WhooingOAuthError",
    "WhooingPydanticError",
    "WhooingPydanticUnavailableError",
    "WhooingRateLimitError",
    "WhooingResponseError",
    "WhooingTransportError",
]
