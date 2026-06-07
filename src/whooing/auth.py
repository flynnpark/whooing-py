from __future__ import annotations

import base64
import hashlib
import secrets
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import cast
from urllib.parse import urlencode

import httpx

from whooing.exceptions import WhooingOAuthError, WhooingResponseError, WhooingTransportError
from whooing.types import Headers, JsonObject, JsonValue, RequestData


class Auth:
    def headers(self) -> Headers:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class APIKeyAuth(Auth):
    api_key: str

    def headers(self) -> Headers:
        return {"X-API-KEY": self.api_key}


@dataclass(frozen=True, slots=True)
class BearerTokenAuth(Auth):
    access_token: str

    def headers(self) -> Headers:
        return {"Authorization": f"Bearer {self.access_token}"}


@dataclass(frozen=True, slots=True)
class OAuth1aAuth(Auth):
    app_id: str
    app_secret: str
    token: str
    token_secret: str

    def headers(self) -> Headers:
        signature = hashlib.sha1(f"{self.app_secret}|{self.token_secret}".encode()).hexdigest()
        nonce = secrets.token_hex(20)
        timestamp = str(int(time.time()))
        value = ",".join(
            (
                f"app_id={self.app_id}",
                f"token={self.token}",
                f"signature={signature}",
                f"nounce={nonce}",
                f"timestamp={timestamp}",
            )
        )
        return {"X-API-KEY": value}


@dataclass(frozen=True, slots=True)
class PKCEChallenge:
    verifier: str
    challenge: str
    method: str = "S256"


@dataclass(frozen=True, slots=True)
class OAuth2Token:
    access_token: str
    token_type: str
    expires_in: int | None
    refresh_token: str | None
    scope: str | None
    raw: JsonObject


@dataclass(frozen=True, slots=True)
class OAuth1RequestToken:
    token: str
    raw: JsonObject


@dataclass(frozen=True, slots=True)
class OAuth1AccessToken:
    token: str
    token_secret: str
    user_id: int | None
    raw: JsonObject


class OAuth2TokenClient:
    def __init__(
        self,
        *,
        token_endpoint: str = "https://whooing.com/oauth2/token",
        revoke_endpoint: str = "https://whooing.com/oauth2/revoke",
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._token_endpoint = token_endpoint
        self._revoke_endpoint = revoke_endpoint
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OAuth2TokenClient:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def exchange_code(
        self,
        *,
        client_id: str,
        code: str,
        redirect_uri: str,
        code_verifier: str | None = None,
    ) -> OAuth2Token:
        data: dict[str, str] = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if code_verifier is not None:
            data["code_verifier"] = code_verifier
        return self._post_token(data)

    def refresh(self, *, client_id: str, refresh_token: str) -> OAuth2Token:
        return self._post_token(
            {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "refresh_token": refresh_token,
            }
        )

    def revoke(self, token: str) -> JsonObject:
        return self._post_json(self._revoke_endpoint, {"token": token})

    def _post_token(self, data: RequestData) -> OAuth2Token:
        return _parse_oauth2_token(self._post_json(self._token_endpoint, data))

    def _post_json(self, url: str, data: RequestData) -> JsonObject:
        try:
            response = self._client.post(url, data={key: value for key, value in data.items()})
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc
        return _decode_oauth_json(response)


class AppAuthClient:
    def __init__(
        self,
        *,
        base_url: str = "https://whooing.com/app_auth/",
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout, transport=transport)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AppAuthClient:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def request_token(
        self,
        *,
        app_id: str,
        app_secret: str,
        callback_uri: str | None = None,
    ) -> OAuth1RequestToken:
        params: dict[str, str] = {"app_id": app_id, "app_secret": app_secret}
        if callback_uri is not None:
            params["callbackuri"] = callback_uri
        return _parse_oauth1_request_token(self._get_json("request_token", params))

    def build_authorization_url(
        self,
        *,
        token: str,
        callback_uri: str | None = None,
        no_register: bool = False,
    ) -> str:
        params: dict[str, str] = {"token": token}
        if callback_uri is not None:
            params["callbackuri"] = callback_uri
        if no_register:
            params["no_register"] = "y"
        return str(self._client.base_url.join("authorize").copy_with(params=params))

    def access_token(
        self,
        *,
        app_id: str,
        app_secret: str,
        token: str,
        pin: str,
    ) -> OAuth1AccessToken:
        return _parse_oauth1_access_token(
            self._get_json(
                "access_token",
                {
                    "app_id": app_id,
                    "app_secret": app_secret,
                    "token": token,
                    "pin": pin,
                },
            )
        )

    def access_token_by_onetime(
        self,
        *,
        app_id: str,
        app_secret: str,
        onetime_pin: str,
    ) -> OAuth1AccessToken:
        return _parse_oauth1_access_token(
            self._get_json(
                "access_token_by_onetime",
                {
                    "app_id": app_id,
                    "app_secret": app_secret,
                    "onetime_pin": onetime_pin,
                },
            )
        )

    def _get_json(self, path: str, params: RequestData) -> JsonObject:
        try:
            response = self._client.get(path, params={key: value for key, value in params.items()})
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc
        return _decode_oauth_json(response)


class AsyncOAuth2TokenClient:
    def __init__(
        self,
        *,
        token_endpoint: str = "https://whooing.com/oauth2/token",
        revoke_endpoint: str = "https://whooing.com/oauth2/revoke",
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._token_endpoint = token_endpoint
        self._revoke_endpoint = revoke_endpoint
        self._client = httpx.AsyncClient(timeout=timeout, transport=transport)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncOAuth2TokenClient:
        return self

    async def __aexit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        await self.close()

    async def exchange_code(
        self,
        *,
        client_id: str,
        code: str,
        redirect_uri: str,
        code_verifier: str | None = None,
    ) -> OAuth2Token:
        data: dict[str, str] = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        if code_verifier is not None:
            data["code_verifier"] = code_verifier
        return await self._post_token(data)

    async def refresh(self, *, client_id: str, refresh_token: str) -> OAuth2Token:
        return await self._post_token(
            {
                "grant_type": "refresh_token",
                "client_id": client_id,
                "refresh_token": refresh_token,
            }
        )

    async def revoke(self, token: str) -> JsonObject:
        return await self._post_json(self._revoke_endpoint, {"token": token})

    async def _post_token(self, data: RequestData) -> OAuth2Token:
        return _parse_oauth2_token(await self._post_json(self._token_endpoint, data))

    async def _post_json(self, url: str, data: RequestData) -> JsonObject:
        try:
            response = await self._client.post(
                url,
                data={key: value for key, value in data.items()},
            )
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc
        return _decode_oauth_json(response)


class AsyncAppAuthClient:
    def __init__(
        self,
        *,
        base_url: str = "https://whooing.com/app_auth/",
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=transport)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncAppAuthClient:
        return self

    async def __aexit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        await self.close()

    async def request_token(
        self,
        *,
        app_id: str,
        app_secret: str,
        callback_uri: str | None = None,
    ) -> OAuth1RequestToken:
        params: dict[str, str] = {"app_id": app_id, "app_secret": app_secret}
        if callback_uri is not None:
            params["callbackuri"] = callback_uri
        return _parse_oauth1_request_token(await self._get_json("request_token", params))

    def build_authorization_url(
        self,
        *,
        token: str,
        callback_uri: str | None = None,
        no_register: bool = False,
    ) -> str:
        params: dict[str, str] = {"token": token}
        if callback_uri is not None:
            params["callbackuri"] = callback_uri
        if no_register:
            params["no_register"] = "y"
        return str(self._client.base_url.join("authorize").copy_with(params=params))

    async def access_token(
        self,
        *,
        app_id: str,
        app_secret: str,
        token: str,
        pin: str,
    ) -> OAuth1AccessToken:
        return _parse_oauth1_access_token(
            await self._get_json(
                "access_token",
                {
                    "app_id": app_id,
                    "app_secret": app_secret,
                    "token": token,
                    "pin": pin,
                },
            )
        )

    async def access_token_by_onetime(
        self,
        *,
        app_id: str,
        app_secret: str,
        onetime_pin: str,
    ) -> OAuth1AccessToken:
        return _parse_oauth1_access_token(
            await self._get_json(
                "access_token_by_onetime",
                {
                    "app_id": app_id,
                    "app_secret": app_secret,
                    "onetime_pin": onetime_pin,
                },
            )
        )

    async def _get_json(self, path: str, params: RequestData) -> JsonObject:
        try:
            response = await self._client.get(
                path,
                params={key: value for key, value in params.items()},
            )
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc
        return _decode_oauth_json(response)


def create_pkce_challenge(byte_length: int = 64) -> PKCEChallenge:
    verifier = secrets.token_urlsafe(byte_length)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return PKCEChallenge(verifier=verifier, challenge=challenge)


def build_authorization_url(
    *,
    client_id: str,
    redirect_uri: str,
    scopes: Iterable[str] = (),
    state: str | None = None,
    challenge: PKCEChallenge | None = None,
    authorization_endpoint: str = "https://whooing.com/oauth2/authorize",
) -> str:
    params: dict[str, str] = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    scope_value = ",".join(scopes)
    if scope_value:
        params["scope"] = scope_value
    if state is not None:
        params["state"] = state
    if challenge is not None:
        params["code_challenge"] = challenge.challenge
        params["code_challenge_method"] = challenge.method
    return f"{authorization_endpoint}?{urlencode(params)}"


def get_oauth2_metadata(
    *,
    metadata_url: str = "https://whooing.com/.well-known/oauth-authorization-server",
    timeout: float | httpx.Timeout = 10.0,
    transport: httpx.BaseTransport | None = None,
) -> JsonObject:
    with httpx.Client(timeout=timeout, transport=transport) as client:
        try:
            response = client.get(metadata_url)
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc
    return _decode_oauth_json(response)


async def async_get_oauth2_metadata(
    *,
    metadata_url: str = "https://whooing.com/.well-known/oauth-authorization-server",
    timeout: float | httpx.Timeout = 10.0,
    transport: httpx.AsyncBaseTransport | None = None,
) -> JsonObject:
    async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
        try:
            response = await client.get(metadata_url)
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc
    return _decode_oauth_json(response)


def _decode_oauth_json(response: httpx.Response) -> JsonObject:
    try:
        payload = cast(JsonObject, response.json())
    except ValueError as exc:
        raise WhooingResponseError(
            "Whooing OAuth response is not valid JSON.",
            status_code=response.status_code,
            body=response.text,
        ) from exc

    error = _optional_str(payload.get("error"))
    if error is not None:
        raise WhooingOAuthError(error, _optional_str(payload.get("error_description")))

    if response.status_code >= 400:
        raise WhooingResponseError(
            f"Whooing OAuth response failed with status {response.status_code}.",
            status_code=response.status_code,
            body=response.text,
        )

    return payload


def _parse_oauth2_token(payload: JsonObject) -> OAuth2Token:
    access_token = _optional_str(payload.get("access_token"))
    token_type = _optional_str(payload.get("token_type"))
    if access_token is None or token_type is None:
        raise WhooingOAuthError(
            "invalid_token_response",
            "access_token and token_type are required",
        )
    return OAuth2Token(
        access_token=access_token,
        token_type=token_type,
        expires_in=_optional_int(payload.get("expires_in")),
        refresh_token=_optional_str(payload.get("refresh_token")),
        scope=_optional_str(payload.get("scope")),
        raw=payload,
    )


def _parse_oauth1_request_token(payload: JsonObject) -> OAuth1RequestToken:
    token = _optional_str(payload.get("token"))
    if token is None:
        raise WhooingOAuthError("invalid_token_response", "token is required")
    return OAuth1RequestToken(token=token, raw=payload)


def _parse_oauth1_access_token(payload: JsonObject) -> OAuth1AccessToken:
    token = _optional_str(payload.get("token"))
    token_secret = _optional_str(payload.get("token_secret"))
    if token is None or token_secret is None:
        raise WhooingOAuthError(
            "invalid_token_response",
            "token and token_secret are required",
        )
    return OAuth1AccessToken(
        token=token,
        token_secret=token_secret,
        user_id=_optional_int(payload.get("user_id")),
        raw=payload,
    )


def _optional_str(value: JsonValue | None) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _optional_int(value: JsonValue | None) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None
