from __future__ import annotations

import httpx

from helpers import form_body, make_client


def test_sections_sort_uses_documented_path_and_comma_values() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.method == "PUT"
        assert request.url.path == "/api/sections/sort.json"
        assert form_body(request) == {"section_ids": ["s1,s2"]}

    client = make_client(assert_request)

    assert client.sections.sort(["s1", "s2"]).results == {"ok": True}


def test_entries_bulk_create_serializes_entries_as_json_string() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.method == "POST"
        assert request.url.path == "/api/entries.json"
        body = form_body(request)
        assert body["section_id"] == ["s1"]
        assert body["data_type"] == ["json"]
        assert '"item":"커피"' in body["entries"][0].replace(" ", "")

    client = make_client(assert_request)

    client.entries.create_many(
        section_id="s1",
        entries=[
            {
                "entry_date": 20260607,
                "l_account": "expenses",
                "l_account_id": "x1",
                "r_account": "assets",
                "r_account_id": "x2",
                "item": "커피",
                "money": 5000,
                "memo": "",
            }
        ],
    )


def test_budget_update_uses_account_id_keys() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.method == "PUT"
        assert request.url.path == "/api/budget/expenses.json"
        assert form_body(request) == {
            "section_id": ["s1"],
            "target_ym": ["202606"],
            "x12": ["100000"],
        }

    client = make_client(assert_request)

    client.budgets.update("expenses", section_id="s1", target_ym=202606, budgets={"x12": 100000})


def test_report_path_variants() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.method == "GET"
        assert request.url.path == "/api/report/expenses,xincome/x1.json"
        assert request.url.params["section_id"] == "s1"

    client = make_client(assert_request)

    client.reports.report("expenses,xincome", "x1", section_id="s1")


def test_upload_uses_mimetype_parameter_name_from_docs() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.method == "GET"
        assert request.url.path == "/api/upload.json"
        assert request.url.params["mimeType"] == "image/jpeg"

    client = make_client(assert_request)

    client.extras.prepare_upload(name="receipt.jpg", mime_type="image/jpeg", size=10)
