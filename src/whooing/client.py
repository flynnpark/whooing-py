from __future__ import annotations

import time

import httpx

from whooing._transport import (
    DEFAULT_BASE_URL,
    HttpMethod,
    clean_params,
    decode_api_response,
    request_with_retries,
    resolve_auth,
)
from whooing.auth import Auth
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

SyncApiResponse = ApiResponse[JsonValue]


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
        response = request_with_retries(
            lambda: self._client.request(
                method,
                path,
                params=clean_params(params),
                data=clean_params(data),
                headers=headers,
            ),
            retry_policy=self._retry_policy,
            sleep=time.sleep,
        )
        return decode_api_response(response)

    def get(self, path: str, *, params: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("GET", path, params=params)

    def post(self, path: str, *, data: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("POST", path, data=data)

    def put(self, path: str, *, data: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("PUT", path, data=data)

    def delete(self, path: str, *, data: RequestData | None = None) -> ApiResponse[JsonValue]:
        return self.request("DELETE", path, data=data)
