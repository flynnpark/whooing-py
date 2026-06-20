from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Literal, cast

import httpx

from whooing.auth import APIKeyAuth, Auth, BearerTokenAuth
from whooing.exceptions import WhooingRateLimitError, WhooingResponseError, WhooingTransportError
from whooing.response import ApiResponse, parse_api_response
from whooing.retry import RetryPolicy
from whooing.types import JsonObject, JsonValue, RequestData, RequestValue

HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
DEFAULT_BASE_URL = "https://whooing.com/api/"
SyncSend = Callable[[], httpx.Response]
SyncSleep = Callable[[float], None]
AsyncSend = Callable[[], Awaitable[httpx.Response]]
AsyncSleep = Callable[[float], Awaitable[None]]


def resolve_auth(
    *,
    auth: Auth | None,
    api_key: str | None,
    access_token: str | None,
) -> Auth:
    provided = [auth is not None, api_key is not None, access_token is not None]
    if sum(provided) != 1:
        raise ValueError("Provide exactly one of auth, api_key, or access_token.")
    if auth is not None:
        return auth
    if api_key is not None:
        return APIKeyAuth(api_key)
    if access_token is not None:
        return BearerTokenAuth(access_token)
    raise ValueError("Authentication is required.")


def clean_params(data: RequestData | None) -> Mapping[str, RequestValue] | None:
    if data is None:
        return None
    return {key: value for key, value in data.items() if value is not None}


def request_with_retries(
    send: SyncSend,
    *,
    retry_policy: RetryPolicy | None,
    sleep: SyncSleep,
) -> httpx.Response:
    attempt = 1
    while True:
        try:
            response = send()
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc

        if retry_policy is None or not retry_policy.should_retry(response, attempt):
            return response

        delay = retry_policy.delay_for(response, attempt)
        if delay > 0:
            sleep(delay)
        attempt += 1


async def async_request_with_retries(
    send: AsyncSend,
    *,
    retry_policy: RetryPolicy | None,
    sleep: AsyncSleep,
) -> httpx.Response:
    attempt = 1
    while True:
        try:
            response = await send()
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc

        if retry_policy is None or not retry_policy.should_retry(response, attempt):
            return response

        delay = retry_policy.delay_for(response, attempt)
        if delay > 0:
            await sleep(delay)
        attempt += 1


def decode_api_response(response: httpx.Response) -> ApiResponse[JsonValue]:
    if response.status_code == 429:
        raise WhooingRateLimitError(
            "Whooing HTTP response failed with status 429.",
            code=429,
            rest_of_api=None,
            error_parameters={},
            http_status_code=response.status_code,
            retry_after=_parse_retry_after(response.headers.get("Retry-After")),
        )

    if response.status_code >= 400:
        raise WhooingResponseError(
            f"Whooing HTTP response failed with status {response.status_code}.",
            status_code=response.status_code,
            body=response.text,
        )

    try:
        payload = cast(JsonObject, response.json())
    except ValueError as exc:
        raise WhooingResponseError(
            "Whooing response is not valid JSON.",
            status_code=response.status_code,
            body=response.text,
        ) from exc

    return parse_api_response(payload)


def _parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
