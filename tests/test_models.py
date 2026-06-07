from __future__ import annotations

from urllib.parse import parse_qs

import httpx

from whooing import EntryInput, WhooingClient


def test_entry_input_serializes_documented_fields() -> None:
    entry = EntryInput(
        entry_date=20260607,
        left_account="expenses",
        left_account_id="x1",
        right_account="assets",
        right_account_id="x2",
        item="커피",
        money=5000,
        memo="",
    )

    assert entry.to_request_data() == {
        "entry_date": 20260607,
        "l_account": "expenses",
        "l_account_id": "x1",
        "r_account": "assets",
        "r_account_id": "x2",
        "item": "커피",
        "money": 5000,
        "memo": "",
    }


def test_entries_resource_accepts_entry_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/entries.json"
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        assert body["entry_date"] == ["20260607"]
        assert body["l_account"] == ["expenses"]
        assert body["r_account"] == ["assets"]
        return httpx.Response(200, json={"code": 200, "results": {"entry_id": 1}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.entries.create_entry(
        section_id="s1",
        entry=EntryInput(
            entry_date=20260607,
            left_account="expenses",
            left_account_id="x1",
            right_account="assets",
            right_account_id="x2",
            item="커피",
            money=5000,
        ),
    )

    assert response.results == {"entry_id": 1}
