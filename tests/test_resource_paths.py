from __future__ import annotations

import httpx

from helpers import form_body, make_client


def test_user_logs_path() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.method == "GET"
        assert request.url.path == "/api/user_logs.json"
        assert request.url.params["start_date"] == "20260601"

    make_client(assert_request).users.logs(start_date=20260601)


def test_section_crud_paths() -> None:
    calls: list[tuple[str, str]] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append((request.method, request.url.path))

    client = make_client(assert_request)

    client.sections.get("s1")
    client.sections.update("s1", title="개인")
    client.sections.delete(["s1", "s2"])

    assert calls == [
        ("GET", "/api/sections/s1.json"),
        ("PUT", "/api/sections/s1.json"),
        ("DELETE", "/api/sections/s1,s2.json"),
    ]


def test_account_paths() -> None:
    calls: list[tuple[str, str]] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append((request.method, request.url.path))

    client = make_client(assert_request)

    client.accounts.list_by_type("assets", section_id="s1")
    client.accounts.get("assets", "x1", section_id="s1")
    client.accounts.exists("assets", "x1", section_id="s1")
    client.accounts.update("assets", "x1", section_id="s1", title="현금")
    client.accounts.delete("assets", "x1", section_id="s1")
    client.accounts.sort("assets", section_id="s1", account_ids=["x1", "x2"])

    assert calls == [
        ("GET", "/api/accounts/assets.json"),
        ("GET", "/api/accounts/assets/x1.json"),
        ("GET", "/api/accounts/assets/x1/exists.json"),
        ("PUT", "/api/accounts/assets/x1.json"),
        ("DELETE", "/api/accounts/assets/x1/s1.json"),
        ("PUT", "/api/accounts/assets/sort.json"),
    ]


def test_entry_analysis_paths() -> None:
    calls: list[str] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append(request.url.path)

    client = make_client(assert_request)

    client.entries.flow_of_account(section_id="s1")
    client.entries.flow_of_account_id(section_id="s1")
    client.entries.changes_of_account_id(section_id="s1")
    client.entries.changes_of_client(section_id="s1")
    client.entries.changes_of_item(section_id="s1")
    client.entries.account_ids_of_account(section_id="s1")
    client.entries.clients_of_account_id(section_id="s1")
    client.entries.items_of_account_id(section_id="s1")

    assert calls == [
        "/api/entries/flow_of_account.json",
        "/api/entries/flow_of_account_id.json",
        "/api/entries/changes_of_account_id.json",
        "/api/entries/changes_of_client.json",
        "/api/entries/changes_of_item.json",
        "/api/entries/account_ids_of_account.json",
        "/api/entries/clients_of_account_id.json",
        "/api/entries/items_of_account_id.json",
    ]


def test_entry_update_delete_and_outside_paths() -> None:
    calls: list[tuple[str, str]] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append((request.method, request.url.path))

    client = make_client(assert_request)

    client.entries.update_many([1, 2], section_id="s1", item="수정")
    client.entries.delete([1, 2], section_id="s1")
    client.entries.parse_outside(section_id="s1", rows="row")
    client.entries.report_outside_source("bank")

    assert calls == [
        ("PUT", "/api/entries/1,2/s1.json"),
        ("DELETE", "/api/entries/1,2/s1.json"),
        ("POST", "/api/entries/outside.json"),
        ("POST", "/api/entries/outside_report.json"),
    ]


def test_budget_goal_paths() -> None:
    calls: list[tuple[str, str]] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append((request.method, request.url.path))

    client = make_client(assert_request)

    client.budgets.get_goal(section_id="s1")
    client.budgets.update_goal(section_id="s1", start_date=202601)
    client.budgets.delete_goal(section_id="s1")
    client.budgets.get_capital_goal(section_id="s1")
    client.budgets.update_capital_goal(section_id="s1", monthly_goals={1: 1000})

    assert calls == [
        ("GET", "/api/budget_goal.json"),
        ("PUT", "/api/budget_goal.json"),
        ("DELETE", "/api/budget_goal.json"),
        ("GET", "/api/goal.json"),
        ("PUT", "/api/goal.json"),
    ]


def test_report_paths() -> None:
    calls: list[str] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append(request.url.path)

    client = make_client(assert_request)

    client.reports.report()
    client.reports.report("expenses")
    client.reports.summary()
    client.reports.summary("expenses")
    client.reports.custom_rows(section_id="s1", report="report_bs")
    client.reports.update_custom_rows(
        section_id="s1",
        report="report_bs",
        action="post",
        row="{}",
    )

    assert calls == [
        "/api/report.json",
        "/api/report/expenses.json",
        "/api/report_summary.json",
        "/api/report_summary/expenses.json",
        "/api/main/report_customs.json",
        "/api/main/report_customs.json",
    ]


def test_extras_remaining_paths() -> None:
    calls: list[tuple[str, str]] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append((request.method, request.url.path))

    client = make_client(assert_request)

    client.extras.bill()
    client.extras.bill("x1")
    client.extras.checkcard()
    client.extras.checkcard("x1")
    client.extras.in_out("assets", "x1")
    client.extras.calendar(section_id="s1")
    client.extras.unread_messages()
    client.extras.notifications(section_id="s1")
    client.extras.mark_notifications_read()
    client.extras.monthly_items_slot()

    assert calls == [
        ("GET", "/api/bill.json"),
        ("GET", "/api/bill/x1.json"),
        ("GET", "/api/checkcard.json"),
        ("GET", "/api/checkcard/x1.json"),
        ("GET", "/api/in_out/assets/x1.json"),
        ("GET", "/api/calendar.json"),
        ("GET", "/api/messages/unread.json"),
        ("GET", "/api/notifications.json"),
        ("PUT", "/api/notifications.json"),
        ("GET", "/api/monthly_items/slot1.json"),
    ]


def test_bbs_delete_and_recommendation_paths() -> None:
    calls: list[tuple[str, str]] = []

    def assert_request(request: httpx.Request) -> None:
        calls.append((request.method, request.url.path))

    client = make_client(assert_request)

    client.extras.delete_bbs("notice", [1, 2])
    client.extras.delete_bbs_comment("notice", 1, ["c1", "c2"])
    client.extras.delete_bbs_reply("notice", 1, "c1", [10, 20])
    client.extras.recommend_bbs(bbs_id=1, comment_id="c1")

    assert calls == [
        ("DELETE", "/api/bbs/notice/1,2.json"),
        ("DELETE", "/api/bbs/notice/1/c1,c2.json"),
        ("DELETE", "/api/bbs/notice/1/c1/10,20.json"),
        ("PUT", "/api/bbs/recommandation.json"),
    ]


def test_null_params_are_removed_before_request() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert request.url.path == "/api/notifications.json"
        assert "section_id" not in request.url.params

    make_client(assert_request).extras.notifications(section_id=None)


def test_request_body_removes_none_values() -> None:
    def assert_request(request: httpx.Request) -> None:
        assert form_body(request) == {"title": ["개인"]}

    make_client(assert_request).sections.create(title="개인", memo=None)
