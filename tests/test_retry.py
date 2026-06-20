from __future__ import annotations

import asyncio

import httpx
import pytest

from whooing import AsyncWhooingClient, RetryPolicy, WhooingClient, WhooingRateLimitError
from whooing.retry import parse_retry_after


def test_sync_client_retries_rate_limit_response() -> None:
    attempts = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, json={"message": "rate limited"})
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(
        api_key="secret",
        transport=httpx.MockTransport(handler),
        retry_policy=RetryPolicy(max_attempts=2),
    )

    response = client.users.get()

    assert attempts == 2
    assert response.results == {"ok": True}


def test_sync_client_keeps_default_no_retry_behavior() -> None:
    attempts = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(429, json={"message": "rate limited"})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingRateLimitError):
        client.users.get()

    assert attempts == 1


def test_async_client_retries_temporary_server_error() -> None:
    async def run() -> None:
        attempts = 0

        async def handler(_: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                return httpx.Response(503, json={"message": "unavailable"})
            return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

        client = AsyncWhooingClient(
            api_key="secret",
            transport=httpx.MockTransport(handler),
            retry_policy=RetryPolicy(max_attempts=2),
        )

        try:
            response = await client.users.get()
        finally:
            await client.close()

        assert attempts == 2
        assert response.results == {"ok": True}

    asyncio.run(run())


def test_retry_policy_uses_retry_after_header() -> None:
    policy = RetryPolicy(max_attempts=2, backoff_seconds=10.0)
    response = httpx.Response(429, headers={"Retry-After": "3"})

    assert policy.delay_for(response, 1) == 3.0


def test_retry_after_parser_rejects_negative_values() -> None:
    assert parse_retry_after("-1") is None
