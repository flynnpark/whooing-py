from __future__ import annotations

from urllib.parse import parse_qs

import httpx

from whooing import (
    AccountInput,
    BasicTotalBudgetInput,
    BudgetInput,
    EntryInput,
    MessageInput,
    PostItInput,
    WhooingClient,
)


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


def test_account_input_serializes_optional_fields() -> None:
    account = AccountInput(
        title="현금",
        memo="지갑",
        open_date=20260101,
        currency="KRW",
        initial_money=10000,
    )

    assert account.to_request_data() == {
        "title": "현금",
        "memo": "지갑",
        "open_date": 20260101,
        "currency": "KRW",
        "initial_money": 10000,
    }


def test_accounts_resource_accepts_account_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/accounts/assets.json"
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        assert body["title"] == ["현금"]
        assert body["currency"] == ["KRW"]
        return httpx.Response(200, json={"code": 200, "results": {"account_id": "x1"}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.accounts.create_account(
        "assets",
        section_id="s1",
        account_input=AccountInput(title="현금", currency="KRW"),
    )

    assert response.results == {"account_id": "x1"}


def test_budget_inputs_serialize_documented_dynamic_keys() -> None:
    budget = BudgetInput(target_ym=202606, amounts_by_account_id={"x1": 10000})
    total = BasicTotalBudgetInput(
        start_date=202601,
        end_date=202612,
        monthly_totals={1: 10000, 12: 20000},
    )

    assert budget.to_request_data() == {"target_ym": 202606, "x1": 10000}
    assert total.to_request_data() == {
        "start_date": 202601,
        "end_date": 202612,
        "1": 10000,
        "12": 20000,
    }


def test_budget_resource_accepts_budget_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/api/budget/expenses.json"
        body = parse_qs(request.content.decode())
        assert body == {
            "section_id": ["s1"],
            "target_ym": ["202606"],
            "x1": ["10000"],
        }
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.budgets.update_budget(
        "expenses",
        section_id="s1",
        budget=BudgetInput(target_ym=202606, amounts_by_account_id={"x1": 10000}),
    )

    assert response.results == {"ok": True}


def test_post_it_input_serializes_optional_fields() -> None:
    post_it = PostItInput(
        section_id="s1",
        title="메모",
        contents="내용",
        position="10,20",
        color="yellow",
    )

    assert post_it.to_request_data() == {
        "section_id": "s1",
        "title": "메모",
        "contents": "내용",
        "position": "10,20",
        "color": "yellow",
    }


def test_extras_resource_accepts_post_it_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/post_it.json"
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        assert body["title"] == ["메모"]
        assert body["contents"] == ["내용"]
        return httpx.Response(200, json={"code": 200, "results": {"post_it_id": 1}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.extras.create_post_it_from(
        PostItInput(section_id="s1", title="메모", contents="내용")
    )

    assert response.results == {"post_it_id": 1}


def test_message_input_serializes_multiple_user_ids() -> None:
    message = MessageInput(opponent_user_ids=[1, "2"], message="안녕하세요")

    assert message.to_request_data() == {
        "opponent_user_ids": "1,2",
        "message": "안녕하세요",
    }


def test_extras_resource_accepts_message_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/messages.json"
        body = parse_qs(request.content.decode())
        assert body["opponent_user_ids"] == ["1,2"]
        assert body["message"] == ["안녕하세요"]
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.extras.send_message_from(
        MessageInput(opponent_user_ids=[1, "2"], message="안녕하세요")
    )

    assert response.results == {"ok": True}
