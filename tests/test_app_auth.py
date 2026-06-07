from __future__ import annotations

import asyncio

import httpx

from whooing import AppAuthClient, AsyncAppAuthClient
from whooing.auth import async_get_oauth2_metadata, get_oauth2_metadata


def test_app_auth_request_token_uses_legacy_endpoint_params() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/app_auth/request_token"
        assert request.url.params["app_id"] == "app"
        assert request.url.params["app_secret"] == "secret"
        assert request.url.params["callbackuri"] == "https://example.com/callback"
        return httpx.Response(200, json={"token": "request-token"})

    client = AppAuthClient(transport=httpx.MockTransport(handler))

    token = client.request_token(
        app_id="app",
        app_secret="secret",
        callback_uri="https://example.com/callback",
    )

    assert token.token == "request-token"


def test_app_auth_access_token_and_authorization_url() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/app_auth/access_token"
        assert request.url.params["token"] == "request-token"
        assert request.url.params["pin"] == "123456"
        return httpx.Response(
            200,
            json={
                "code": 200,
                "token": "access-token",
                "token_secret": "token-secret",
                "user_id": 2399,
            },
        )

    client = AppAuthClient(transport=httpx.MockTransport(handler))

    url = client.build_authorization_url(
        token="request-token",
        callback_uri="https://example.com/callback",
        no_register=True,
    )
    token = client.access_token(
        app_id="app",
        app_secret="secret",
        token="request-token",
        pin="123456",
    )

    assert "token=request-token" in url
    assert "no_register=y" in url
    assert token.token == "access-token"
    assert token.token_secret == "token-secret"
    assert token.user_id == 2399


def test_app_auth_onetime_pin() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/app_auth/access_token_by_onetime"
        assert request.url.params["onetime_pin"] == "123456"
        return httpx.Response(
            200,
            json={"token": "access-token", "token_secret": "token-secret"},
        )

    client = AppAuthClient(transport=httpx.MockTransport(handler))

    token = client.access_token_by_onetime(
        app_id="app",
        app_secret="secret",
        onetime_pin="123456",
    )

    assert token.token == "access-token"


def test_oauth2_metadata_helper() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://whooing.com/.well-known/oauth-authorization-server"
        return httpx.Response(
            200,
            json={"authorization_endpoint": "https://whooing.com/oauth2/authorize"},
        )

    metadata = get_oauth2_metadata(transport=httpx.MockTransport(handler))

    assert metadata["authorization_endpoint"] == "https://whooing.com/oauth2/authorize"


def test_async_app_auth_and_metadata_helpers() -> None:
    async def run() -> None:
        async def app_handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"token": "request-token"})

        async def metadata_handler(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"token_endpoint": "https://whooing.com/oauth2/token"})

        async with AsyncAppAuthClient(transport=httpx.MockTransport(app_handler)) as client:
            token = await client.request_token(app_id="app", app_secret="secret")

        metadata = await async_get_oauth2_metadata(transport=httpx.MockTransport(metadata_handler))

        assert token.token == "request-token"
        assert metadata["token_endpoint"] == "https://whooing.com/oauth2/token"

    asyncio.run(run())
