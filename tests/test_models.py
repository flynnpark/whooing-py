from __future__ import annotations

from urllib.parse import parse_qs

import httpx
import pytest

from whooing import (
    AccountInput,
    BasicTotalBudgetInput,
    BbsCommentInput,
    BbsPostInput,
    BudgetGoalInput,
    BudgetInput,
    CapitalGoalInput,
    EntryInput,
    FrequentItemInput,
    MessageInput,
    MonthlyItemInput,
    PostItInput,
    SectionInput,
    UserInput,
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
        account_type="account",
        open_date=20260101,
        close_date=29991231,
        title="현금",
        memo="지갑",
        category="normal",
    )

    assert account.to_request_data() == {
        "type": "account",
        "open_date": 20260101,
        "close_date": 29991231,
        "title": "현금",
        "memo": "지갑",
        "category": "normal",
    }


def test_accounts_resource_accepts_account_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/accounts/assets.json"
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        assert body["title"] == ["현금"]
        assert body["type"] == ["account"]
        assert body["close_date"] == ["29991231"]
        return httpx.Response(200, json={"code": 200, "results": {"account_id": "x1"}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.accounts.create_account(
        "assets",
        section_id="s1",
        account_input=AccountInput(
            account_type="account",
            open_date=20260101,
            close_date=29991231,
            title="현금",
        ),
    )

    assert response.results == {"account_id": "x1"}


def test_budget_inputs_serialize_documented_dynamic_keys() -> None:
    budget = BudgetInput(target_ym=202606, amounts_by_account_id={"x1": 10000})
    monthly_totals = {month: month * 1000 for month in range(1, 13)}
    total = BasicTotalBudgetInput(
        start_date=202601,
        end_date=202612,
        monthly_totals=monthly_totals,
    )

    assert budget.to_request_data() == {"target_ym": 202606, "x1": 10000}
    assert total.to_request_data() == {
        "start_date": 202601,
        "end_date": 202612,
        **{str(month): amount for month, amount in monthly_totals.items()},
    }


def test_basic_total_budget_requires_all_twelve_months() -> None:
    with pytest.raises(ValueError, match="every month from 1 through 12"):
        BasicTotalBudgetInput(
            start_date=202601,
            end_date=202612,
            monthly_totals={1: 10000},
        )


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
        page="_main/index",
        contents="내용",
        everywhere="n",
        color="ffbd94",
    )

    assert post_it.to_request_data() == {
        "section_id": "s1",
        "page": "_main/index",
        "contents": "내용",
        "everywhere": "n",
        "color": "ffbd94",
    }


def test_extras_resource_accepts_post_it_input() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/post_it.json"
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        assert body["page"] == ["_main/index"]
        assert body["contents"] == ["내용"]
        return httpx.Response(200, json={"code": 200, "results": {"post_it_id": 1}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.extras.create_post_it_from(
        PostItInput(section_id="s1", page="_main/index", contents="내용")
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


def test_section_input_and_resource_helper() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/sections.json"
        body = parse_qs(request.content.decode())
        assert body["title"] == ["개인"]
        assert body["currency"] == ["KRW"]
        return httpx.Response(200, json={"code": 200, "results": {"section_id": "s1"}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.sections.create_section(SectionInput(title="개인", currency="KRW"))

    assert response.results == {"section_id": "s1"}


def test_frequent_and_monthly_item_inputs() -> None:
    frequent = FrequentItemInput(
        section_id="s1",
        item="커피",
        money=5000,
        left_account="expenses",
        left_account_id="x1",
        right_account="assets",
        right_account_id="x2",
        extra_fields={"custom": "value"},
    )
    monthly = MonthlyItemInput(
        section_id="s1",
        item="월세",
        pay_date=27,
        money=500000,
        skip_holiday="after",
    )

    assert frequent.to_request_data()["custom"] == "value"
    assert frequent.to_request_data()["l_account"] == "expenses"
    assert monthly.to_request_data()["pay_date"] == 27


def test_extras_resource_accepts_frequent_and_monthly_item_inputs() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        assert body["item"]
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    client.extras.create_frequent_item_from(
        "slot1",
        FrequentItemInput(
            section_id="s1",
            item="커피",
            left_account="expenses",
            right_account="assets",
        ),
    )
    client.extras.create_monthly_item_from(
        MonthlyItemInput(section_id="s1", item="월세", pay_date=27)
    )

    assert calls == ["/api/frequent_items/slot1.json", "/api/monthly_items/slot1.json"]


def test_bbs_inputs_and_resource_helpers() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        body = parse_qs(request.content.decode())
        assert body
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    client.extras.create_bbs_from(
        "notice",
        BbsPostInput(subject="제목", contents="본문", extra_fields={"tag": "api"}),
    )
    client.extras.create_bbs_comment_from(
        "notice",
        1,
        BbsCommentInput(contents="댓글"),
    )
    client.extras.create_bbs_reply_from(
        "notice",
        1,
        "c1",
        BbsCommentInput(contents="답글"),
    )

    assert calls == [
        "/api/bbs/notice.json",
        "/api/bbs/notice/1.json",
        "/api/bbs/notice/1/c1.json",
    ]


def test_user_input_and_resource_helper() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/api/user.json"
        body = parse_qs(request.content.decode())
        assert body["username"] == ["flynn"]
        assert body["language"] == ["ko"]
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    response = client.users.update_user(UserInput(username="flynn", language="ko"))

    assert response.results == {"ok": True}


def test_goal_inputs_and_resource_helpers() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        body = parse_qs(request.content.decode())
        assert body["section_id"] == ["s1"]
        return httpx.Response(200, json={"code": 200, "results": {"ok": True}})

    client = WhooingClient(api_key="secret", transport=httpx.MockTransport(handler))

    client.budgets.update_goal_from(
        section_id="s1",
        goal=BudgetGoalInput(
            base_ym=202601,
            goal_ym=202712,
            goal_money=50_000_000,
            split_type="equal",
        ),
    )
    client.budgets.update_capital_goal_from(
        section_id="s1",
        goal=CapitalGoalInput(monthly_goals={1: 10000, "12": 120000}),
    )

    assert calls == ["/api/budget_goal.json", "/api/goal.json"]
