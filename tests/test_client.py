from __future__ import annotations

import httpx
import pytest

from whooing import WhooingAuthError, WhooingClient, WhooingRateLimitError, WhooingResponseError
from whooing.auth import build_authorization_url, create_pkce_challenge


def test_get_sends_api_key_and_returns_response_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-KEY"] == "secret"
        assert request.url == "https://whooing.com/api/sections.json"
        return httpx.Response(
            200,
            json={
                "code": 200,
                "message": "",
                "rest_of_api": 4988,
                "error_parameters": {},
                "results": [{"section_id": "s1"}],
            },
        )

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.get("sections.json")

    assert response.code == 200
    assert response.rest_of_api == 4988
    assert response.results == [{"section_id": "s1"}]


def test_bearer_token_authentication() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"code": 200, "results": {"user_id": 1}})

    client = WhooingClient(access_token="token", transport=httpx.MockTransport(handler))

    assert client.get("user.json").results == {"user_id": 1}


def test_api_error_maps_auth_code() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "code": 405,
                "message": "token expired",
                "rest_of_api": 10,
                "error_parameters": {},
            },
        )

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingAuthError):
        client.get("user.json")


def test_api_error_maps_rate_limit_code() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "code": 402,
                "message": "quota exceeded",
                "rest_of_api": 0,
                "error_parameters": {},
            },
        )

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingRateLimitError):
        client.get("user.json")


def test_http_429_raises_rate_limit_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="Too Many Requests")

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingRateLimitError):
        client.get("user.json")


def test_http_error_raises_response_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Server Error")

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    with pytest.raises(WhooingResponseError):
        client.get("user.json")


def test_pkce_authorization_url_contains_challenge() -> None:
    challenge = create_pkce_challenge()

    url = build_authorization_url(
        client_id="app",
        redirect_uri="http://localhost/callback",
        scopes=["read", "write"],
        state="state",
        challenge=challenge,
    )

    assert "response_type=code" in url
    assert "client_id=app" in url
    assert "scope=read%2Cwrite" in url
    assert f"code_challenge={challenge.challenge}" in url
