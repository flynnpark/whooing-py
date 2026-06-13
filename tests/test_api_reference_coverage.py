from __future__ import annotations

import re
from dataclasses import dataclass, field

from whooing.resources import (
    AccountsResource,
    BudgetResource,
    EntriesResource,
    ExtrasResource,
    ReportsResource,
    SectionsResource,
    UsersResource,
)
from whooing.types import RequestData

DOCUMENTED_API_ENDPOINTS: frozenset[tuple[str, str]] = frozenset(
    {
        ("GET", "user.json"),
        ("PUT", "user.json"),
        ("GET", "user_logs.json"),
        ("GET", "user_point_logs.json"),
        ("GET", "sections.json"),
        ("GET", "sections/:section_id.json"),
        ("POST", "sections.json"),
        ("PUT", "sections/:section_id.json"),
        ("DELETE", "sections/:section_id.json"),
        ("GET", "sections/default.json"),
        ("PUT", "sections/sort.json"),
        ("GET", "accounts.json"),
        ("GET", "accounts/:account.json"),
        ("GET", "accounts/:account/:account_id.json"),
        ("GET", "accounts/:account/:account_id/exists.json"),
        ("POST", "accounts/:account.json"),
        ("PUT", "accounts/:account/:account_id.json"),
        ("DELETE", "accounts/:account/:account_id/:section_id.json"),
        ("PUT", "accounts/:account/sort.json"),
        ("GET", "entries.json"),
        ("GET", "entries/:entry_id.json"),
        ("POST", "entries.json"),
        ("PUT", "entries/:entry_id.json"),
        ("PUT", "entries/:entry_ids/:section_id.json"),
        ("DELETE", "entries/:entry_ids/:section_id.json"),
        ("GET", "entries/latest.json"),
        ("GET", "entries/latest_items.json"),
        ("GET", "entries/flow_of_account.json"),
        ("GET", "entries/flow_of_account_id.json"),
        ("GET", "entries/changes_of_account_id.json"),
        ("GET", "entries/changes_of_client.json"),
        ("GET", "entries/changes_of_item.json"),
        ("GET", "entries/account_ids_of_account.json"),
        ("GET", "entries/clients_of_account_id.json"),
        ("GET", "entries/items_of_account_id.json"),
        ("POST", "entries/outside.json"),
        ("POST", "entries/outside_report.json"),
        ("GET", "frequent_items.json"),
        ("GET", "frequent_items/:slot.json"),
        ("GET", "frequent_items/:slot/:item_id.json"),
        ("POST", "frequent_items/:slot.json"),
        ("PUT", "frequent_items/:slot/:item_id.json"),
        ("DELETE", "frequent_items/:slot/:item_id/:section_id.json"),
        ("PUT", "frequent_items/:slot/sort.json"),
        ("GET", "monthly_items.json"),
        ("GET", "monthly_items/slot1.json"),
        ("GET", "monthly_items/slot1/:item_id.json"),
        ("POST", "monthly_items/slot1.json"),
        ("PUT", "monthly_items/slot1/:item_id.json"),
        ("DELETE", "monthly_items/slot1/:item_id/:section_id.json"),
        ("GET", "budget/:account.json"),
        ("PUT", "budget/:account.json"),
        ("PUT", "budget/:account/basic_total.json"),
        ("DELETE", "budget/:account.json"),
        ("GET", "budget_goal.json"),
        ("PUT", "budget_goal.json"),
        ("DELETE", "budget_goal.json"),
        ("GET", "bill.json"),
        ("GET", "bill/:account_id.json"),
        ("GET", "checkcard.json"),
        ("GET", "checkcard/:account_id.json"),
        ("GET", "in_out.json"),
        ("GET", "in_out/:account.json"),
        ("GET", "in_out/:account/:account_id.json"),
        ("GET", "calendar.json"),
        ("GET", "report.json"),
        ("GET", "report/:account.json"),
        ("GET", "report/:account/:account_id.json"),
        ("GET", "report_summary.json"),
        ("GET", "report_summary/:account.json"),
        ("GET", "main/report_customs.json"),
        ("POST", "main/report_customs.json"),
        ("GET", "goal.json"),
        ("PUT", "goal.json"),
        ("GET", "post_it.json"),
        ("GET", "post_it/:post_it_id.json"),
        ("POST", "post_it.json"),
        ("PUT", "post_it/:post_it_id.json"),
        ("DELETE", "post_it/:section_id/:post_it_id.json"),
        ("GET", "messages.json"),
        ("GET", "messages/:opponent_user_id.json"),
        ("POST", "messages.json"),
        ("DELETE", "messages/:opponent_user_id.json"),
        ("GET", "messages/unread.json"),
        ("GET", "bbs.json"),
        ("GET", "bbs/:category.json"),
        ("GET", "bbs/:category/:bbs_id.json"),
        ("POST", "bbs/:category.json"),
        ("PUT", "bbs/:category/:bbs_id.json"),
        ("DELETE", "bbs/:category/:bbs_id.json"),
        ("GET", "bbs/:category/:bbs_id/:comment_id.json"),
        ("POST", "bbs/:category/:bbs_id.json"),
        ("PUT", "bbs/:category/:bbs_id/:comment_id.json"),
        ("DELETE", "bbs/:category/:bbs_id/:comment_id.json"),
        ("POST", "bbs/:category/:bbs_id/:comment_id.json"),
        ("DELETE", "bbs/:category/:bbs_id/:comment_id/:addition_id.json"),
        ("PUT", "bbs/recommandation.json"),
        ("GET", "upload.json"),
        ("POST", "upload.json"),
        ("GET", "notifications.json"),
        ("PUT", "notifications.json"),
    }
)


@dataclass
class RecordingClient:
    calls: set[tuple[str, str]] = field(default_factory=set)

    def get(self, path: str, *, params: RequestData | None = None) -> object:
        self._record("GET", path)
        return object()

    def post(self, path: str, *, data: RequestData | None = None) -> object:
        self._record("POST", path)
        return object()

    def put(self, path: str, *, data: RequestData | None = None) -> object:
        self._record("PUT", path)
        return object()

    def delete(self, path: str, *, data: RequestData | None = None) -> object:
        self._record("DELETE", path)
        return object()

    def _record(self, method: str, path: str) -> None:
        self.calls.add((method, _normalize_path(path)))


def test_all_documented_api_endpoints_are_implemented() -> None:
    implemented = _collect_implemented_api_endpoints()

    assert implemented == DOCUMENTED_API_ENDPOINTS
    assert len(DOCUMENTED_API_ENDPOINTS) == 101


def _collect_implemented_api_endpoints() -> frozenset[tuple[str, str]]:
    client = RecordingClient()

    users = UsersResource[object](client)
    sections = SectionsResource[object](client)
    accounts = AccountsResource[object](client)
    entries = EntriesResource[object](client)
    budgets = BudgetResource[object](client)
    reports = ReportsResource[object](client)
    extras = ExtrasResource[object](client)

    users.get()
    users.update(nickname="flynn")
    users.logs()
    users.point_logs()

    sections.list()
    sections.get("s1")
    sections.create(title="개인")
    sections.update("s1", title="개인")
    sections.delete("s1")
    sections.default()
    sections.sort(["s1", "s2"])

    accounts.list(section_id="s1")
    accounts.list_by_type("assets", section_id="s1")
    accounts.get("assets", "x1", section_id="s1")
    accounts.exists("assets", "x1", section_id="s1")
    accounts.create("assets", section_id="s1", title="현금")
    accounts.update("assets", "x1", section_id="s1", title="현금")
    accounts.delete("assets", "x1", section_id="s1")
    accounts.sort("assets", section_id="s1", account_ids=["x1", "x2"])

    entries.list(section_id="s1")
    entries.get("e1", section_id="s1")
    entries.create(section_id="s1", item="커피")
    entries.update("e1", section_id="s1", item="커피")
    entries.update_many(["e1", "e2"], section_id="s1", item="커피")
    entries.delete(["e1", "e2"], section_id="s1")
    entries.latest(section_id="s1")
    entries.latest_items(section_id="s1")
    entries.flow_of_account(section_id="s1")
    entries.flow_of_account_id(section_id="s1")
    entries.changes_of_account_id(section_id="s1")
    entries.changes_of_client(section_id="s1")
    entries.changes_of_item(section_id="s1")
    entries.account_ids_of_account(section_id="s1")
    entries.clients_of_account_id(section_id="s1")
    entries.items_of_account_id(section_id="s1")
    entries.parse_outside(section_id="s1", rows="row")
    entries.report_outside_source("bank")

    budgets.get("assets", section_id="s1")
    budgets.update("assets", section_id="s1", target_ym=202606, budgets={"x1": 100})
    budgets.update_basic_total(
        "assets",
        section_id="s1",
        start_date=202601,
        end_date=202612,
        monthly_totals={1: 100},
    )
    budgets.delete("assets", section_id="s1", start_date=202601, end_date=202612)
    budgets.get_goal(section_id="s1")
    budgets.update_goal(section_id="s1", start_date=202601)
    budgets.delete_goal(section_id="s1")
    budgets.get_capital_goal(section_id="s1")
    budgets.update_capital_goal(section_id="s1", monthly_goals={1: 100})

    reports.report()
    reports.report("assets")
    reports.report("assets", "x1")
    reports.summary()
    reports.summary("assets")
    reports.custom_rows(section_id="s1", report="report_bs")
    reports.update_custom_rows(section_id="s1", report="report_bs", action="post", row="{}")

    extras.frequent_items()
    extras.frequent_items("slot1")
    extras.frequent_items("slot1", "i1")
    extras.create_frequent_item("slot1", item="커피")
    extras.update_frequent_item("slot1", "i1", item="커피")
    extras.delete_frequent_item("slot1", "i1", "s1")
    extras.sort_frequent_items("slot1", section_id="s1", item_ids=["i1", "i2"])
    extras.monthly_items()
    extras.monthly_items_slot("slot1")
    extras.monthly_items("m1", slot="slot1")
    extras.create_monthly_item(item="월세")
    extras.update_monthly_item("m1", item="월세")
    extras.delete_monthly_item("m1", "s1")
    extras.bill()
    extras.bill("x1")
    extras.checkcard()
    extras.checkcard("x1")
    extras.in_out()
    extras.in_out("assets")
    extras.in_out("assets", "x1")
    extras.calendar()
    extras.post_its()
    extras.post_its("p1")
    extras.create_post_it(title="메모")
    extras.update_post_it("p1", title="메모")
    extras.delete_post_it("s1", "p1")
    extras.messages()
    extras.messages("u1")
    extras.send_message(opponent_user_ids="u1", message="hello")
    extras.delete_messages("u1")
    extras.unread_messages()
    extras.bbs()
    extras.bbs("notice")
    extras.bbs("notice", "b1")
    extras.bbs("notice", "b1", "c1")
    extras.create_bbs("notice", title="공지")
    extras.update_bbs("notice", "b1", title="공지")
    extras.delete_bbs("notice", "b1")
    extras.create_bbs_comment("notice", "b1", contents="댓글")
    extras.update_bbs_comment("notice", "b1", "c1", contents="댓글")
    extras.delete_bbs_comment("notice", "b1", "c1")
    extras.create_bbs_reply("notice", "b1", "c1", contents="답글")
    extras.delete_bbs_reply("notice", "b1", "c1", "r1")
    extras.recommend_bbs(bbs_id="b1", comment_id="c1")
    extras.prepare_upload(name="receipt.jpg", mime_type="image/jpeg", size=1)
    extras.complete_upload("uuid1")
    extras.notifications()
    extras.mark_notifications_read()

    return frozenset(client.calls)


def _normalize_path(path: str) -> str:
    for pattern, replacement in _PATH_PATTERNS:
        if re.fullmatch(pattern, path):
            return replacement
    return path


_PATH_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"sections/s1\.json", "sections/:section_id.json"),
    (r"accounts/assets\.json", "accounts/:account.json"),
    (r"accounts/assets/x1\.json", "accounts/:account/:account_id.json"),
    (r"accounts/assets/x1/exists\.json", "accounts/:account/:account_id/exists.json"),
    (r"accounts/assets/x1/s1\.json", "accounts/:account/:account_id/:section_id.json"),
    (r"accounts/assets/sort\.json", "accounts/:account/sort.json"),
    (r"entries/e1\.json", "entries/:entry_id.json"),
    (r"entries/e1,e2/s1\.json", "entries/:entry_ids/:section_id.json"),
    (r"frequent_items/slot1\.json", "frequent_items/:slot.json"),
    (r"frequent_items/slot1/i1\.json", "frequent_items/:slot/:item_id.json"),
    (
        r"frequent_items/slot1/i1/s1\.json",
        "frequent_items/:slot/:item_id/:section_id.json",
    ),
    (r"frequent_items/slot1/sort\.json", "frequent_items/:slot/sort.json"),
    (r"monthly_items/slot1/m1\.json", "monthly_items/slot1/:item_id.json"),
    (r"monthly_items/slot1/m1/s1\.json", "monthly_items/slot1/:item_id/:section_id.json"),
    (r"budget/assets\.json", "budget/:account.json"),
    (r"budget/assets/basic_total\.json", "budget/:account/basic_total.json"),
    (r"bill/x1\.json", "bill/:account_id.json"),
    (r"checkcard/x1\.json", "checkcard/:account_id.json"),
    (r"in_out/assets\.json", "in_out/:account.json"),
    (r"in_out/assets/x1\.json", "in_out/:account/:account_id.json"),
    (r"report/assets\.json", "report/:account.json"),
    (r"report/assets/x1\.json", "report/:account/:account_id.json"),
    (r"report_summary/assets\.json", "report_summary/:account.json"),
    (r"post_it/p1\.json", "post_it/:post_it_id.json"),
    (r"post_it/s1/p1\.json", "post_it/:section_id/:post_it_id.json"),
    (r"messages/u1\.json", "messages/:opponent_user_id.json"),
    (r"bbs/notice\.json", "bbs/:category.json"),
    (r"bbs/notice/b1\.json", "bbs/:category/:bbs_id.json"),
    (r"bbs/notice/b1/c1\.json", "bbs/:category/:bbs_id/:comment_id.json"),
    (
        r"bbs/notice/b1/c1/r1\.json",
        "bbs/:category/:bbs_id/:comment_id/:addition_id.json",
    ),
)
