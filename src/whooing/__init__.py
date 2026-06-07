"""Typed Python client library for the Whooing Developer API."""

from whooing.async_client import AsyncWhooingClient
from whooing.auth import APIKeyAuth, BearerTokenAuth, OAuth1aAuth
from whooing.client import WhooingClient
from whooing.exceptions import (
    WhooingAPIError,
    WhooingAuthError,
    WhooingError,
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
    "BearerTokenAuth",
    "OAuth1aAuth",
    "WhooingAPIError",
    "WhooingAuthError",
    "WhooingClient",
    "WhooingError",
    "WhooingRateLimitError",
    "WhooingResponseError",
    "WhooingTransportError",
]
