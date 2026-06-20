from __future__ import annotations

import asyncio
from urllib.parse import parse_qs

import httpx
import pytest

from whooing import (
    AsyncOAuth2TokenClient,
    OAuth2TokenClient,
    WhooingOAuthError,
    WhooingResponseError,
)


def test_oauth2_exchange_code_posts_documented_form_fields() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://whooing.com/oauth2/token"
        body = parse_qs(request.content.decode())
        assert body == {
            "grant_type": ["authorization_code"],
            "client_id": ["app"],
            "code": ["code"],
            "redirect_uri": ["http://localhost/callback"],
            "code_verifier": ["verifier"],
        }
        return httpx.Response(
            200,
            json={
                "access_token": "access",
                "token_type": "Bearer",
                "expires_in": 31536000,
                "refresh_token": "refresh",
                "scope": "read,write",
            },
        )

    client = OAuth2TokenClient(transport=httpx.MockTransport(handler))

    token = client.exchange_code(
        client_id="app",
        code="code",
        redirect_uri="http://localhost/callback",
        code_verifier="verifier",
    )

    assert token.access_token == "access"
    assert token.refresh_token == "refresh"


def test_oauth2_error_payload_raises_oauth_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={"error": "invalid_grant", "error_description": "expired"},
        )

    client = OAuth2TokenClient(transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingOAuthError) as exc_info:
        client.refresh(client_id="app", refresh_token="refresh")

    assert exc_info.value.error == "invalid_grant"
    assert exc_info.value.description == "expired"


def test_oauth2_non_json_http_error_raises_response_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="<html>Server Error</html>")

    client = OAuth2TokenClient(transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingResponseError) as exc_info:
        client.refresh(client_id="app", refresh_token="refresh")

    assert exc_info.value.status_code == 500
    assert exc_info.value.body == "<html>Server Error</html>"


def test_async_oauth2_refresh() -> None:
    async def run() -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            body = parse_qs(request.content.decode())
            assert body["grant_type"] == ["refresh_token"]
            return httpx.Response(
                200,
                json={
                    "access_token": "new-access",
                    "token_type": "Bearer",
                    "refresh_token": "new-refresh",
                },
            )

        async with AsyncOAuth2TokenClient(transport=httpx.MockTransport(handler)) as client:
            token = await client.refresh(client_id="app", refresh_token="refresh")

        assert token.access_token == "new-access"
        assert token.refresh_token == "new-refresh"

    asyncio.run(run())
