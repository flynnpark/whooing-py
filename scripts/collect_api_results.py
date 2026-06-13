from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, cast

from dotenv import load_dotenv

from whooing import WhooingClient, WhooingError
from whooing.response import ApiResponse
from whooing.types import JsonObject, JsonValue

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
AccountType = Literal["assets", "liabilities", "capital", "income", "expenses"]
InOutAccountType = Literal["assets", "liabilities"]
ReportCustomType = Literal["report_bs", "report_pl"]

ACCOUNT_TYPES: tuple[AccountType, ...] = (
    "assets",
    "liabilities",
    "capital",
    "income",
    "expenses",
)
IN_OUT_ACCOUNT_TYPES: tuple[InOutAccountType, ...] = ("assets", "liabilities")
REPORT_CUSTOM_TYPES: tuple[ReportCustomType, ...] = ("report_bs", "report_pl")
WRITE_ENDPOINTS = (
    "users.update",
    "sections.create",
    "sections.update",
    "sections.delete",
    "sections.sort",
    "accounts.create",
    "accounts.update",
    "accounts.delete",
    "accounts.sort",
    "entries.create",
    "entries.create_many",
    "entries.update",
    "entries.update_many",
    "entries.delete",
    "entries.parse_outside",
    "entries.report_outside_source",
    "budgets.update",
    "budgets.update_basic_total",
    "budgets.delete",
    "budgets.update_goal",
    "budgets.delete_goal",
    "budgets.update_capital_goal",
    "reports.update_custom_rows",
    "extras.create_frequent_item",
    "extras.update_frequent_item",
    "extras.delete_frequent_item",
    "extras.sort_frequent_items",
    "extras.create_monthly_item",
    "extras.update_monthly_item",
    "extras.delete_monthly_item",
    "extras.create_post_it",
    "extras.update_post_it",
    "extras.delete_post_it",
    "extras.send_message",
    "extras.delete_messages",
    "extras.create_bbs",
    "extras.update_bbs",
    "extras.delete_bbs",
    "extras.create_bbs_comment",
    "extras.update_bbs_comment",
    "extras.delete_bbs_comment",
    "extras.create_bbs_reply",
    "extras.delete_bbs_reply",
    "extras.recommend_bbs",
    "extras.complete_upload",
    "extras.mark_notifications_read",
)
ApiCall = Callable[[], ApiResponse[JsonValue]]


@dataclass(frozen=True, slots=True)
class CollectedResult:
    name: str
    status: str
    raw: JsonObject | None
    error: str | None = None


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = _require_env("WHOOING_API_KEY")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    markdown_path = REPORTS_DIR / f"whooing_api_results_{timestamp}.md"
    json_path = REPORTS_DIR / f"whooing_api_results_{timestamp}.json"

    REPORTS_DIR.mkdir(exist_ok=True)

    with WhooingClient(api_key=api_key) as client:
        results = collect_read_results(client)

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scope": "read_only",
        "results": [result_to_json(result) for result in results],
        "skipped_write_endpoints": list(WRITE_ENDPOINTS),
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")

    print(markdown_path)
    print(json_path)


def collect_read_results(client: WhooingClient) -> list[CollectedResult]:
    results: list[CollectedResult] = []

    def call(name: str, callback: Callable[[], ApiResponse[JsonValue]]) -> JsonValue | None:
        result = collect(name, callback)
        results.append(result)
        if result.raw is None:
            return None
        return result.raw.get("results")

    user = call("users.get", client.users.get)
    call("users.logs", client.users.logs)
    call("users.point_logs", client.users.point_logs)

    sections = call("sections.list", client.sections.list)
    default_section = call("sections.default", client.sections.default)
    section_id = resolve_section_id(sections, default_section)
    configured_section_id = os.environ.get("WHOOING_SECTION_ID")
    if configured_section_id:
        section_id = configured_section_id

    if section_id is None:
        results.append(
            CollectedResult(
                name="section-scoped APIs",
                status="skipped",
                raw=None,
                error="사용 가능한 section_id를 찾지 못해 섹션 기반 조회 API를 건너뜀",
            )
        )
        return results

    call("sections.get", lambda: client.sections.get(section_id))

    accounts = call("accounts.list", lambda: client.accounts.list(section_id=section_id))
    account_ids = account_ids_by_type(accounts)
    for account_type in ACCOUNT_TYPES:
        call(
            f"accounts.list_by_type.{account_type}",
            cast(
                ApiCall,
                lambda account_type=account_type: client.accounts.list_by_type(
                    account_type,
                    section_id=section_id,
                ),
            ),
        )
        account_id = account_ids.get(account_type)
        if account_id is not None:
            call(
                f"accounts.get.{account_type}",
                cast(
                    ApiCall,
                    lambda account_type=account_type, account_id=account_id: client.accounts.get(
                        account_type,
                        account_id,
                        section_id=section_id,
                    ),
                ),
            )
            call(
                f"accounts.exists.{account_type}",
                cast(
                    ApiCall,
                    lambda account_type=account_type, account_id=account_id: client.accounts.exists(
                        account_type,
                        account_id,
                        section_id=section_id,
                    ),
                ),
            )

    entries = call("entries.list", lambda: client.entries.list(section_id=section_id))
    latest_entries = call("entries.latest", lambda: client.entries.latest(section_id=section_id))
    entry_id = resolve_entry_id(entries, latest_entries)
    analytics_account = first_available_account_type(account_ids)
    analytics_account_id = (
        account_ids.get(analytics_account) if analytics_account is not None else None
    )
    if entry_id is not None:
        call("entries.get", lambda: client.entries.get(entry_id, section_id=section_id))

    call("entries.latest_items", lambda: client.entries.latest_items(section_id=section_id))
    if analytics_account is not None:
        call(
            "entries.flow_of_account",
            lambda: client.entries.flow_of_account(
                section_id=section_id,
                account=analytics_account,
            ),
        )
        call(
            "entries.account_ids_of_account",
            lambda: client.entries.account_ids_of_account(
                section_id=section_id,
                account=analytics_account,
            ),
        )
    if analytics_account_id is not None:
        call(
            "entries.flow_of_account_id",
            lambda: client.entries.flow_of_account_id(
                section_id=section_id,
                account=analytics_account,
                account_id=analytics_account_id,
            ),
        )
        call(
            "entries.clients_of_account_id",
            lambda: client.entries.clients_of_account_id(
                section_id=section_id,
                account=analytics_account,
                account_id=analytics_account_id,
            ),
        )
        call(
            "entries.items_of_account_id",
            lambda: client.entries.items_of_account_id(
                section_id=section_id,
                account=analytics_account,
                account_id=analytics_account_id,
            ),
        )
    call(
        "entries.changes_of_account_id",
        lambda: client.entries.changes_of_account_id(section_id=section_id),
    )
    call(
        "entries.changes_of_client",
        lambda: client.entries.changes_of_client(section_id=section_id),
    )
    call("entries.changes_of_item", lambda: client.entries.changes_of_item(section_id=section_id))

    for account_type in ("income", "expenses"):
        call(
            f"budgets.get.{account_type}",
            cast(
                ApiCall,
                lambda account_type=account_type: client.budgets.get(
                    account_type,
                    section_id=section_id,
                ),
            ),
        )

    call("budgets.get_goal", lambda: client.budgets.get_goal(section_id=section_id))
    call("budgets.get_capital_goal", lambda: client.budgets.get_capital_goal(section_id=section_id))

    call(
        "reports.report",
        lambda: client.reports.report(section_id=section_id, rows_type="none"),
    )
    for account_type in ACCOUNT_TYPES:
        call(
            f"reports.report.{account_type}",
            cast(
                ApiCall,
                lambda account_type=account_type: client.reports.report(
                    account_type,
                    section_id=section_id,
                    rows_type="none",
                ),
            ),
        )
    call(
        "reports.summary",
        lambda: client.reports.summary(section_id=section_id, rows_type="none"),
    )
    for account_type in ACCOUNT_TYPES:
        call(
            f"reports.summary.{account_type}",
            cast(
                ApiCall,
                lambda account_type=account_type: client.reports.summary(
                    account_type,
                    section_id=section_id,
                    rows_type="none",
                ),
            ),
        )
    def custom_rows_call(report_name: ReportCustomType) -> ApiCall:
        return lambda: client.reports.custom_rows(
            section_id=section_id,
            report=report_name,
            action="list",
        )

    for report_name in REPORT_CUSTOM_TYPES:
        call(
            f"reports.custom_rows.{report_name}",
            custom_rows_call(report_name),
        )

    frequent_items = call(
        "extras.frequent_items",
        lambda: client.extras.frequent_items(section_id=section_id),
    )
    frequent_item_id = resolve_item_id(frequent_items, "item_id")
    call(
        "extras.frequent_items.slot1",
        lambda: client.extras.frequent_items("slot1", section_id=section_id),
    )
    if frequent_item_id is not None:
        frequent_item_id_str = str(frequent_item_id)
        call(
            "extras.frequent_items.slot1.item",
            lambda: client.extras.frequent_items(
                "slot1",
                frequent_item_id_str,
                section_id=section_id,
            ),
        )

    monthly_items = call(
        "extras.monthly_items",
        lambda: client.extras.monthly_items(section_id=section_id),
    )
    monthly_item_id = resolve_item_id(monthly_items, "item_id")
    call(
        "extras.monthly_items_slot.slot1",
        lambda: client.extras.monthly_items_slot("slot1", section_id=section_id),
    )
    if monthly_item_id is not None:
        monthly_item_id_str = str(monthly_item_id)
        call(
            "extras.monthly_items.slot1.item",
            lambda: client.extras.monthly_items(
                monthly_item_id_str,
                slot="slot1",
                section_id=section_id,
            ),
        )

    call("extras.bill", lambda: client.extras.bill(section_id=section_id))
    call("extras.checkcard", lambda: client.extras.checkcard(section_id=section_id))
    call("extras.in_out", lambda: client.extras.in_out(section_id=section_id))

    def in_out_account_call(account_type: InOutAccountType) -> ApiCall:
        return lambda: client.extras.in_out(
            account_type,
            section_id=section_id,
        )

    def in_out_detail_call(account_type: InOutAccountType, account_id: str) -> ApiCall:
        return lambda: client.extras.in_out(
            account_type,
            account_id,
            section_id=section_id,
        )

    for account_type in IN_OUT_ACCOUNT_TYPES:
        in_out_result = call(
            f"extras.in_out.{account_type}",
            in_out_account_call(account_type),
        )
        account_id = resolve_report_account_id(in_out_result)
        if account_id is not None:
            account_id_str = str(account_id)
            call(
                f"extras.in_out.{account_type}.{account_id_str}",
                in_out_detail_call(account_type, account_id_str),
            )
    call("extras.calendar", lambda: client.extras.calendar(section_id=section_id))

    post_its = call("extras.post_its", lambda: client.extras.post_its(section_id=section_id))
    post_it_id = resolve_item_id(post_its, "post_it_id")
    if post_it_id is not None:
        call(
            "extras.post_its.item",
            lambda: client.extras.post_its(post_it_id, section_id=section_id),
        )

    messages = call("extras.messages", client.extras.messages)
    opponent_user_id = resolve_item_id(messages, "opponent_user_id")
    if opponent_user_id is not None:
        call("extras.messages.opponent", lambda: client.extras.messages(opponent_user_id))
    call("extras.unread_messages", client.extras.unread_messages)

    bbs_posts = call("extras.bbs", client.extras.bbs)
    bbs_ref = resolve_bbs_ref(bbs_posts)
    if bbs_ref is not None:
        category, bbs_id, comment_id = bbs_ref
        call("extras.bbs.category", lambda: client.extras.bbs(category))
        call("extras.bbs.post", lambda: client.extras.bbs(category, bbs_id))
        if comment_id is not None:
            call("extras.bbs.comment", lambda: client.extras.bbs(category, bbs_id, comment_id))

    call(
        "extras.prepare_upload",
        lambda: client.extras.prepare_upload(name="sample.txt", mime_type="text/plain", size=1),
    )
    call("extras.notifications", client.extras.notifications)

    if isinstance(user, dict):
        user.pop("token", None)

    return results


def collect(name: str, callback: Callable[[], ApiResponse[JsonValue]]) -> CollectedResult:
    try:
        response = callback()
    except WhooingError as exc:
        return CollectedResult(name=name, status="error", raw=None, error=str(exc))
    except ValueError as exc:
        return CollectedResult(name=name, status="error", raw=None, error=str(exc))
    return CollectedResult(name=name, status="ok", raw=response.raw)


def resolve_section_id(sections: JsonValue | None, default_section: JsonValue | None) -> str | None:
    default_id = section_id_from(default_section)
    if default_id is not None:
        return default_id
    if isinstance(sections, list):
        for section in sections:
            section_id = section_id_from(section)
            if section_id is not None:
                return section_id
    return None


def section_id_from(value: JsonValue | None) -> str | None:
    if not isinstance(value, dict):
        return None
    section_id = value.get("section_id")
    if isinstance(section_id, str) and section_id:
        return section_id
    return None


def account_ids_by_type(accounts: JsonValue | None) -> dict[str, str]:
    if not isinstance(accounts, dict):
        return {}
    resolved: dict[str, str] = {}
    for account_type in ACCOUNT_TYPES:
        account_list = accounts.get(account_type)
        if not isinstance(account_list, list):
            continue
        for account in account_list:
            if isinstance(account, dict):
                account_id = account.get("account_id")
                if isinstance(account_id, str) and account_id:
                    resolved[account_type] = account_id
                    break
    return resolved


def first_available_account_type(account_ids: Mapping[str, str]) -> str | None:
    for account_type in ACCOUNT_TYPES:
        if account_type in account_ids:
            return account_type
    return None


def resolve_entry_id(*values: JsonValue | None) -> str | int | None:
    for value in values:
        if not isinstance(value, list):
            continue
        for entry in value:
            if isinstance(entry, dict):
                entry_id = entry.get("entry_id")
                if isinstance(entry_id, str | int):
                    return entry_id
    return None


def resolve_item_id(value: JsonValue | None, key: str) -> str | int | None:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                item_id = item.get(key)
                if isinstance(item_id, str | int):
                    return item_id
    return None


def resolve_report_account_id(value: JsonValue | None) -> str | int | None:
    if not isinstance(value, dict):
        return None
    accounts = value.get("accounts")
    if not isinstance(accounts, list):
        return None
    for account in accounts:
        if not isinstance(account, dict):
            continue
        account_id = account.get("account_id")
        if isinstance(account_id, str | int):
            return account_id
    return None


def resolve_bbs_ref(value: JsonValue | None) -> tuple[str, str | int, str | None] | None:
    if not isinstance(value, list):
        return None
    for post in value:
        if not isinstance(post, dict):
            continue
        category = post.get("category")
        bbs_id = post.get("bbs_id")
        if not isinstance(category, str) or not isinstance(bbs_id, str | int):
            continue
        comment_id = None
        comments = post.get("comments")
        if isinstance(comments, list):
            for comment in comments:
                if isinstance(comment, dict):
                    candidate = comment.get("comment_id")
                    if isinstance(candidate, str):
                        comment_id = candidate
                        break
        return category, bbs_id, comment_id
    return None


def result_to_json(result: CollectedResult) -> JsonObject:
    data: JsonObject = {
        "name": result.name,
        "status": result.status,
        "raw": result.raw,
    }
    if result.error is not None:
        data["error"] = result.error
    return data


def render_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# 후잉 API 호출 결과",
        "",
        f"- 생성 시각: `{payload['generated_at']}`",
        "- 범위: 조회성 API만 실행",
        "- 원본 응답: 같은 이름의 JSON 파일 참고",
        "",
        "## 호출 결과 요약",
        "",
        "| API | 상태 | code | rest_of_api | results 요약 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in payload["results"]:
        raw = result.get("raw")
        code = raw.get("code") if isinstance(raw, dict) else ""
        rest_of_api = raw.get("rest_of_api") if isinstance(raw, dict) else ""
        summary = summarize_results(raw.get("results") if isinstance(raw, dict) else None)
        if result["status"] != "ok":
            summary = result.get("error", "")
        lines.append(
            f"| `{result['name']}` | {result['status']} | {code} | {rest_of_api} | {summary} |"
        )

    lines.extend(
        [
            "",
            "## API별 원본 응답",
            "",
        ]
    )
    for result in payload["results"]:
        raw = result.get("raw")
        lines.extend(
            [
                "<details>",
                f"<summary><code>{result['name']}</code> - {result['status']}</summary>",
                "",
            ]
        )
        if isinstance(raw, dict):
            lines.extend(
                [
                    "```json",
                    json.dumps(raw, ensure_ascii=False, indent=2),
                    "```",
                ]
            )
        else:
            lines.extend(
                [
                    "```text",
                    str(result.get("error", "")),
                    "```",
                ]
            )
        lines.extend(["", "</details>", ""])

    lines.extend(
        [
            "",
            "## 미실행 API",
            "",
            "아래 API는 생성, 수정, 삭제, 상태 변경 가능성이 있어 호출하지 않았습니다.",
            "",
        ]
    )
    for endpoint in payload["skipped_write_endpoints"]:
        lines.append(f"- `{endpoint}`")
    lines.append("")
    return "\n".join(lines)


def summarize_results(value: JsonValue | None) -> str:
    if isinstance(value, list):
        return f"list[{len(value)}]"
    if isinstance(value, dict):
        keys = ", ".join(list(value.keys())[:5])
        if len(value) > 5:
            keys = f"{keys}, ..."
        return f"object({keys})"
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise RuntimeError(f"{name} 환경 변수가 필요합니다.")
    return value


if __name__ == "__main__":
    main()
