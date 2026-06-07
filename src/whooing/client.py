from __future__ import annotations

import time
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
from whooing.retry import RetryPolicy
from whooing.types import Headers, JsonValue, RequestData

HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
SyncApiResponse = ApiResponse[JsonValue]

DEFAULT_BASE_URL = "https://whooing.com/api/"


class WhooingClient:
    def __init__(
        self,
        *,
        auth: Auth | None = None,
        api_key: str | None = None,
        access_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float | httpx.Timeout = 10.0,
        transport: httpx.BaseTransport | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        resolved_auth = resolve_auth(auth=auth, api_key=api_key, access_token=access_token)
        self._auth = resolved_auth
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            transport=transport,
            headers={"Accept": "application/json", **dict(resolved_auth.headers())},
        )
        self._retry_policy = retry_policy
        self.users: UsersResource[SyncApiResponse] = UsersResource(self)
        self.sections: SectionsResource[SyncApiResponse] = SectionsResource(self)
        self.accounts: AccountsResource[SyncApiResponse] = AccountsResource(self)
        self.entries: EntriesResource[SyncApiResponse] = EntriesResource(self)
        self.budgets: BudgetResource[SyncApiResponse] = BudgetResource(self)
        self.reports: ReportsResource[SyncApiResponse] = ReportsResource(self)
        self.extras: ExtrasResource[SyncApiResponse] = ExtrasResource(self)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> WhooingClient:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        params: RequestData | None = None,
        data: RequestData | None = None,
        headers: Headers | None = None,
    ) -> ApiResponse[JsonValue]:
        attempt = 1
        while True:
            try:
                response = self._client.request(
                    method,
                    path,
                    params=clean_params(params),
                    data=clean_params(data),
                    headers=headers,
                )
            except httpx.TransportError as exc:
                raise WhooingTransportError(str(exc)) from exc

            if self._retry_policy is None or not self._retry_policy.should_retry(response, attempt):
                break

            delay = self._retry_policy.delay_for(response, attempt)
            if delay > 0:
                time.sleep(delay)
            attempt += 1

        return decode_api_response(response)

    def get(self, path: str, *, params: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, data: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("POST", path, data=data)

    def put(self, path: str, *, data: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("PUT", path, data=data)

    def delete(self, path: str, *, data: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("DELETE", path, data=data)
