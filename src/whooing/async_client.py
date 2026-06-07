from __future__ import annotations

from collections.abc import Awaitable
from typing import Literal, cast

import httpx

from whooing.auth import APIKeyAuth, Auth, BearerTokenAuth
from whooing.exceptions import WhooingResponseError, WhooingTransportError
from whooing.resources import (
    AccountsResource,
    BudgetResource,
    EntriesResource,
    ExtrasResource,
    ReportsResource,
    SectionsResource,
    UsersResource,
)
from whooing.response import ApiResponse, parse_api_response
from whooing.types import Headers, JsonObject, JsonValue, RequestData, RequestValue

AsyncHttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
AsyncApiResponse = Awaitable[ApiResponse[JsonValue]]

DEFAULT_BASE_URL = "https://whooing.com/api/"


class AsyncWhooingClient:
    def __init__(
        self,
        *,
        auth: Auth | None = None,
        api_key: str | None = None,
        access_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        resolved_auth = _resolve_auth(auth=auth, api_key=api_key, access_token=access_token)
        self._auth = resolved_auth
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
            headers={"Accept": "application/json", **dict(resolved_auth.headers())},
        )
        self.users = UsersResource[AsyncApiResponse](self)
        self.sections = SectionsResource[AsyncApiResponse](self)
        self.accounts = AccountsResource[AsyncApiResponse](self)
        self.entries = EntriesResource[AsyncApiResponse](self)
        self.budgets = BudgetResource[AsyncApiResponse](self)
        self.reports = ReportsResource[AsyncApiResponse](self)
        self.extras = ExtrasResource[AsyncApiResponse](self)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncWhooingClient:
        return self

    async def __aexit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        await self.close()

    async def request(
        self,
        method: AsyncHttpMethod,
        path: str,
        *,
        params: RequestData | None = None,
        data: RequestData | None = None,
        headers: Headers | None = None,
    ) -> ApiResponse[JsonValue]:
        try:
            response = await self._client.request(
                method,
                path,
                params=_clean_params(params),
                data=_clean_params(data),
                headers=headers,
            )
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc

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

    def get(
        self,
        path: str,
        *,
        params: RequestData | None = None,
    ) -> AsyncApiResponse:
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        data: RequestData | None = None,
    ) -> AsyncApiResponse:
        return self.request("POST", path, data=data)

    def put(
        self,
        path: str,
        *,
        data: RequestData | None = None,
    ) -> AsyncApiResponse:
        return self.request("PUT", path, data=data)

    def delete(
        self,
        path: str,
        *,
        data: RequestData | None = None,
    ) -> AsyncApiResponse:
        return self.request("DELETE", path, data=data)


def _resolve_auth(
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


def _clean_params(data: RequestData | None) -> dict[str, RequestValue] | None:
    if data is None:
        return None
    return {key: value for key, value in data.items() if value is not None}
