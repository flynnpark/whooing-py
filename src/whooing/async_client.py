from __future__ import annotations

from collections.abc import Awaitable
from typing import Literal

import httpx

from whooing._transport import clean_params, decode_api_response, resolve_auth
from whooing.auth import Auth
from whooing.exceptions import WhooingTransportError
from whooing.resources import (
    AccountsResource,
    BudgetResource,
    EntriesResource,
    ExtrasResource,
    ReportsResource,
    SectionsResource,
    UsersResource,
)
from whooing.response import ApiResponse
from whooing.types import Headers, JsonValue, RequestData

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
        resolved_auth = resolve_auth(auth=auth, api_key=api_key, access_token=access_token)
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
                params=clean_params(params),
                data=clean_params(data),
                headers=headers,
            )
        except httpx.TransportError as exc:
            raise WhooingTransportError(str(exc)) from exc

        return decode_api_response(response)

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
