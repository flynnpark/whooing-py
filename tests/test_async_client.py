from __future__ import annotations

import asyncio

import httpx

from whooing import AsyncWhooingClient


def test_async_client_uses_shared_resource_methods() -> None:
    async def run() -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["X-API-KEY"] == "secret"
            assert request.method == "GET"
            assert request.url.path == "/api/sections.json"
            return httpx.Response(200, json={"code": 200, "results": [{"section_id": "s1"}]})

        async with AsyncWhooingClient(
            api_key="secret",
            transport=httpx.MockTransport(handler),
        ) as client:
            response = await client.sections.list()

        assert response.results == [{"section_id": "s1"}]

    asyncio.run(run())
