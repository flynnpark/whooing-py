from __future__ import annotations

from collections.abc import Callable
from urllib.parse import parse_qs

import httpx

from whooing import WhooingClient


def make_client(assert_request: Callable[[httpx.Request], None]) -> WhooingClient:
    def handler(request: httpx.Request) -> httpx.Response:
        assert_request(request)
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    return WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))


def form_body(request: httpx.Request) -> dict[str, list[str]]:
    return parse_qs(request.content.decode())
