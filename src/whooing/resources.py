from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Generic, Literal, Protocol, TypeVar

from whooing.models import (
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
)
from whooing.types import JsonValue, RequestData, RequestValue

ResponseT = TypeVar("ResponseT", covariant=True)


class ResourceClient(Protocol[ResponseT]):
    def get(self, path: str, *, params: RequestData | None = None) -> ResponseT: ...

    def post(self, path: str, *, data: RequestData | None = None) -> ResponseT: ...

    def put(self, path: str, *, data: RequestData | None = None) -> ResponseT: ...

    def delete(self, path: str, *, data: RequestData | None = None) -> ResponseT: ...


class BaseResource(Generic[ResponseT]):
    def __init__(self, client: ResourceClient[ResponseT]) -> None:
        self._client = client


class UsersResource(BaseResource[ResponseT]):
    def get(self) -> ResponseT:
        return self._client.get("user.json")

    def update(self, **fields: RequestValue) -> ResponseT:
        return self._client.put("user.json", data=fields)

    def update_user(self, user: UserInput) -> ResponseT:
        return self.update(**user.to_request_data())

    def logs(self, **params: RequestValue) -> ResponseT:
        return self._client.get("user_logs.json", params=params)

    def point_logs(self, **params: RequestValue) -> ResponseT:
        return self._client.get("user_point_logs.json", params=params)


class SectionsResource(BaseResource[ResponseT]):
    def list(self) -> ResponseT:
        return self._client.get("sections.json")

    def get(self, section_id: str) -> ResponseT:
        return self._client.get(f"sections/{section_id}.json")

    def create(self, **fields: RequestValue) -> ResponseT:
        return self._client.post("sections.json", data=fields)

    def create_section(self, section: SectionInput) -> ResponseT:
        return self.create(**section.to_request_data())

    def update(self, section_id: str, **fields: RequestValue) -> ResponseT:
        return self._client.put(f"sections/{section_id}.json", data=fields)

    def update_section(self, section_id: str, section: SectionInput) -> ResponseT:
        return self.update(section_id, **section.to_request_data())

    def delete(self, section_ids: str | Sequence[str]) -> ResponseT:
        return self._client.delete(f"sections/{_comma_join(section_ids)}.json")

    def default(self) -> ResponseT:
        return self._client.get("sections/default.json")

    def sort(self, section_ids: Sequence[str]) -> ResponseT:
        return self._client.put(
            "sections/sort.json",
            data={"section_ids": _comma_join(section_ids)},
        )


class AccountsResource(BaseResource[ResponseT]):
    def list(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get("accounts.json", params=_with_section(section_id, params))

    def list_by_type(
        self,
        account: str,
        *,
        section_id: str,
        **params: RequestValue,
    ) -> ResponseT:
        return self._client.get(
            f"accounts/{account}.json",
            params=_with_section(section_id, params),
        )

    def get(self, account: str, account_id: str, *, section_id: str) -> ResponseT:
        return self._client.get(
            f"accounts/{account}/{account_id}.json",
            params={"section_id": section_id},
        )

    def exists(self, account: str, account_id: str, *, section_id: str) -> ResponseT:
        return self._client.get(
            f"accounts/{account}/{account_id}/exists.json",
            params={"section_id": section_id},
        )

    def create(self, account: str, *, section_id: str, **fields: RequestValue) -> ResponseT:
        return self._client.post(
            f"accounts/{account}.json",
            data={"section_id": section_id, **fields},
        )

    def create_account(
        self,
        account: str,
        *,
        section_id: str,
        account_input: AccountInput,
    ) -> ResponseT:
        return self.create(account, section_id=section_id, **account_input.to_request_data())

    def update(
        self,
        account: str,
        account_id: str,
        *,
        section_id: str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.put(
            f"accounts/{account}/{account_id}.json",
            data={"section_id": section_id, **fields},
        )

    def update_account(
        self,
        account: str,
        account_id: str,
        *,
        section_id: str,
        account_input: AccountInput,
    ) -> ResponseT:
        return self.update(
            account,
            account_id,
            section_id=section_id,
            **account_input.to_request_data(),
        )

    def delete(self, account: str, account_id: str, *, section_id: str) -> ResponseT:
        return self._client.delete(f"accounts/{account}/{account_id}/{section_id}.json")

    def sort(self, account: str, *, section_id: str, account_ids: Sequence[str]) -> ResponseT:
        return self._client.put(
            f"accounts/{account}/sort.json",
            data={"section_id": section_id, "account_ids": _comma_join(account_ids)},
        )


class EntriesResource(BaseResource[ResponseT]):
    def list(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get("entries.json", params=_with_section(section_id, params))

    def get(self, entry_id: int | str, *, section_id: str) -> ResponseT:
        return self._client.get(f"entries/{entry_id}.json", params={"section_id": section_id})

    def create(self, *, section_id: str, **fields: RequestValue) -> ResponseT:
        return self._client.post("entries.json", data={"section_id": section_id, **fields})

    def create_entry(self, *, section_id: str, entry: EntryInput) -> ResponseT:
        return self.create(section_id=section_id, **entry.to_request_data())

    def create_many(
        self,
        *,
        section_id: str,
        entries: Sequence[Mapping[str, JsonValue]],
    ) -> ResponseT:
        return self._client.post(
            "entries.json",
            data={
                "section_id": section_id,
                "data_type": "json",
                "entries": json.dumps(list(entries), ensure_ascii=False),
            },
        )

    def create_many_entries(self, *, section_id: str, entries: Sequence[EntryInput]) -> ResponseT:
        return self.create_many(
            section_id=section_id,
            entries=[entry.to_json_object() for entry in entries],
        )

    def update(
        self,
        entry_id: int | str,
        *,
        section_id: str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.put(
            f"entries/{entry_id}.json",
            data={"section_id": section_id, **fields},
        )

    def update_many(
        self,
        entry_ids: Sequence[int | str],
        *,
        section_id: str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.put(
            f"entries/{_comma_join(entry_ids)}/{section_id}.json",
            data=fields,
        )

    def delete(self, entry_ids: Sequence[int | str], *, section_id: str) -> ResponseT:
        return self._client.delete(f"entries/{_comma_join(entry_ids)}/{section_id}.json")

    def latest(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get("entries/latest.json", params=_with_section(section_id, params))

    def latest_items(self, *, section_id: str) -> ResponseT:
        return self._client.get("entries/latest_items.json", params={"section_id": section_id})

    def analytics(self, name: str, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get(f"entries/{name}.json", params=_with_section(section_id, params))

    def flow_of_account(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("flow_of_account", section_id=section_id, **params)

    def flow_of_account_id(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("flow_of_account_id", section_id=section_id, **params)

    def changes_of_account_id(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("changes_of_account_id", section_id=section_id, **params)

    def changes_of_client(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("changes_of_client", section_id=section_id, **params)

    def changes_of_item(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("changes_of_item", section_id=section_id, **params)

    def account_ids_of_account(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("account_ids_of_account", section_id=section_id, **params)

    def clients_of_account_id(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("clients_of_account_id", section_id=section_id, **params)

    def items_of_account_id(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self.analytics("items_of_account_id", section_id=section_id, **params)

    def parse_outside(self, *, section_id: str, rows: str) -> ResponseT:
        return self._client.post(
            "entries/outside.json",
            data={"section_id": section_id, "rows": rows},
        )

    def report_outside_source(self, source: str) -> ResponseT:
        return self._client.post("entries/outside_report.json", data={"source": source})


class BudgetResource(BaseResource[ResponseT]):
    def get(self, account: str, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get(
            f"budget/{account}.json",
            params=_with_section(section_id, params),
        )

    def update(
        self,
        account: str,
        *,
        section_id: str,
        target_ym: int | str,
        budgets: Mapping[str, int | float],
    ) -> ResponseT:
        budget_data: dict[str, RequestValue] = {key: value for key, value in budgets.items()}
        return self._client.put(
            f"budget/{account}.json",
            data={"section_id": section_id, "target_ym": target_ym, **budget_data},
        )

    def update_budget(
        self,
        account: str,
        *,
        section_id: str,
        budget: BudgetInput,
    ) -> ResponseT:
        return self._client.put(
            f"budget/{account}.json",
            data={"section_id": section_id, **budget.to_request_data()},
        )

    def update_basic_total(
        self,
        account: str,
        *,
        section_id: str,
        start_date: int | str,
        end_date: int | str,
        monthly_totals: Mapping[int, int | float],
    ) -> ResponseT:
        month_data: dict[str, RequestValue] = {
            str(key): value for key, value in monthly_totals.items()
        }
        return self._client.put(
            f"budget/{account}/basic_total.json",
            data={
                "section_id": section_id,
                "start_date": start_date,
                "end_date": end_date,
                **month_data,
            },
        )

    def update_basic_total_budget(
        self,
        account: str,
        *,
        section_id: str,
        budget: BasicTotalBudgetInput,
    ) -> ResponseT:
        return self._client.put(
            f"budget/{account}/basic_total.json",
            data={"section_id": section_id, **budget.to_request_data()},
        )

    def delete(
        self,
        account: str,
        *,
        section_id: str,
        start_date: int | str,
        end_date: int | str,
    ) -> ResponseT:
        return self._client.delete(
            f"budget/{account}.json",
            data={"section_id": section_id, "start_date": start_date, "end_date": end_date},
        )

    def get_goal(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get("budget_goal.json", params=_with_section(section_id, params))

    def update_goal(self, *, section_id: str, **fields: RequestValue) -> ResponseT:
        return self._client.put("budget_goal.json", data={"section_id": section_id, **fields})

    def update_goal_from(self, *, section_id: str, goal: BudgetGoalInput) -> ResponseT:
        return self.update_goal(section_id=section_id, **goal.to_request_data())

    def delete_goal(self, *, section_id: str) -> ResponseT:
        return self._client.delete("budget_goal.json", data={"section_id": section_id})

    def get_capital_goal(self, *, section_id: str, **params: RequestValue) -> ResponseT:
        return self._client.get("goal.json", params=_with_section(section_id, params))

    def update_capital_goal(
        self,
        *,
        section_id: str,
        monthly_goals: Mapping[int | str, int | float],
    ) -> ResponseT:
        goal_data: dict[str, RequestValue] = {
            str(key): value for key, value in monthly_goals.items()
        }
        return self._client.put("goal.json", data={"section_id": section_id, **goal_data})

    def update_capital_goal_from(
        self,
        *,
        section_id: str,
        goal: CapitalGoalInput,
    ) -> ResponseT:
        return self._client.put(
            "goal.json",
            data={"section_id": section_id, **goal.to_request_data()},
        )


class ReportsResource(BaseResource[ResponseT]):
    def report(
        self,
        account: str | None = None,
        account_id: str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        path = _report_path("report", account, account_id)
        return self._client.get(path, params=params)

    def summary(self, account: str | None = None, **params: RequestValue) -> ResponseT:
        path = "report_summary.json" if account is None else f"report_summary/{account}.json"
        return self._client.get(path, params=params)

    def custom_rows(
        self,
        *,
        section_id: str,
        report: Literal["report_bs", "report_pl"],
        action: Literal["list", "info"] = "list",
        custom_id: int | str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        request_params: dict[str, RequestValue] = {
            "section_id": section_id,
            "report": report,
            "action": action,
            **params,
        }
        if custom_id is not None:
            request_params["customId"] = custom_id
        return self._client.get("main/report_customs.json", params=request_params)

    def update_custom_rows(
        self,
        *,
        section_id: str,
        report: Literal["report_bs", "report_pl"],
        action: Literal["post", "delete", "sort", "clean_disabled"],
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.post(
            "main/report_customs.json",
            data={
                "section_id": section_id,
                "report": report,
                "action": action,
                **fields,
            },
        )


class ExtrasResource(BaseResource[ResponseT]):
    def frequent_items(
        self,
        slot: str | None = None,
        item_id: str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        path = _nested_path("frequent_items", slot, item_id)
        return self._client.get(path, params=params)

    def create_frequent_item(self, slot: str, **fields: RequestValue) -> ResponseT:
        return self._client.post(f"frequent_items/{slot}.json", data=fields)

    def create_frequent_item_from(self, slot: str, item: FrequentItemInput) -> ResponseT:
        return self.create_frequent_item(slot, **item.to_request_data())

    def update_frequent_item(self, slot: str, item_id: str, **fields: RequestValue) -> ResponseT:
        return self._client.put(f"frequent_items/{slot}/{item_id}.json", data=fields)

    def update_frequent_item_from(
        self,
        slot: str,
        item_id: str,
        item: FrequentItemInput,
    ) -> ResponseT:
        return self.update_frequent_item(slot, item_id, **item.to_request_data())

    def delete_frequent_item(
        self,
        slot: str,
        item_ids: str | Sequence[str],
        section_id: str,
    ) -> ResponseT:
        return self._client.delete(
            f"frequent_items/{slot}/{_comma_join(item_ids)}/{section_id}.json"
        )

    def sort_frequent_items(
        self,
        slot: str,
        *,
        section_id: str,
        item_ids: Sequence[str],
    ) -> ResponseT:
        return self._client.put(
            f"frequent_items/{slot}/sort.json",
            data={"section_id": section_id, "item_ids": _comma_join(item_ids)},
        )

    def monthly_items(
        self,
        item_id: str | None = None,
        *,
        slot: str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        if item_id is None and slot is None:
            path = "monthly_items.json"
        elif item_id is None:
            path = f"monthly_items/{slot}.json"
        else:
            path = f"monthly_items/{slot or 'slot1'}/{item_id}.json"
        return self._client.get(path, params=params)

    def monthly_items_slot(self, slot: str = "slot1", **params: RequestValue) -> ResponseT:
        return self._client.get(f"monthly_items/{slot}.json", params=params)

    def create_monthly_item(self, **fields: RequestValue) -> ResponseT:
        return self._client.post("monthly_items/slot1.json", data=fields)

    def create_monthly_item_from(self, item: MonthlyItemInput) -> ResponseT:
        return self.create_monthly_item(**item.to_request_data())

    def update_monthly_item(self, item_id: str, **fields: RequestValue) -> ResponseT:
        return self._client.put(f"monthly_items/slot1/{item_id}.json", data=fields)

    def update_monthly_item_from(self, item_id: str, item: MonthlyItemInput) -> ResponseT:
        return self.update_monthly_item(item_id, **item.to_request_data())

    def delete_monthly_item(self, item_ids: str | Sequence[str], section_id: str) -> ResponseT:
        return self._client.delete(f"monthly_items/slot1/{_comma_join(item_ids)}/{section_id}.json")

    def bill(self, account_id: str | None = None, **params: RequestValue) -> ResponseT:
        path = "bill.json" if account_id is None else f"bill/{account_id}.json"
        return self._client.get(path, params=params)

    def checkcard(self, account_id: str | None = None, **params: RequestValue) -> ResponseT:
        path = "checkcard.json" if account_id is None else f"checkcard/{account_id}.json"
        return self._client.get(path, params=params)

    def in_out(
        self,
        account: str | None = None,
        account_id: str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        path = _report_path("in_out", account, account_id)
        return self._client.get(path, params=params)

    def calendar(self, **params: RequestValue) -> ResponseT:
        return self._client.get("calendar.json", params=params)

    def post_its(
        self,
        post_it_id: int | str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        path = "post_it.json" if post_it_id is None else f"post_it/{post_it_id}.json"
        return self._client.get(path, params=params)

    def create_post_it(self, **fields: RequestValue) -> ResponseT:
        return self._client.post("post_it.json", data=fields)

    def create_post_it_from(self, post_it: PostItInput) -> ResponseT:
        return self.create_post_it(**post_it.to_request_data())

    def update_post_it(self, post_it_id: int | str, **fields: RequestValue) -> ResponseT:
        return self._client.put(f"post_it/{post_it_id}.json", data=fields)

    def update_post_it_from(self, post_it_id: int | str, post_it: PostItInput) -> ResponseT:
        return self.update_post_it(post_it_id, **post_it.to_request_data())

    def delete_post_it(self, section_id: str, post_it_ids: str | Sequence[int | str]) -> ResponseT:
        return self._client.delete(f"post_it/{section_id}/{_comma_join(post_it_ids)}.json")

    def messages(
        self,
        opponent_user_id: int | str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        path = "messages.json" if opponent_user_id is None else f"messages/{opponent_user_id}.json"
        return self._client.get(path, params=params)

    def send_message(
        self,
        *,
        opponent_user_ids: str | Sequence[int | str],
        message: str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.post(
            "messages.json",
            data={
                "opponent_user_ids": _comma_join(opponent_user_ids),
                "message": message,
                **fields,
            },
        )

    def send_message_from(self, message: MessageInput) -> ResponseT:
        return self._client.post("messages.json", data=message.to_request_data())

    def delete_messages(self, opponent_user_id: int | str) -> ResponseT:
        return self._client.delete(f"messages/{opponent_user_id}.json")

    def unread_messages(self) -> ResponseT:
        return self._client.get("messages/unread.json")

    def bbs(
        self,
        category: str | None = None,
        bbs_id: int | str | None = None,
        comment_id: str | None = None,
        **params: RequestValue,
    ) -> ResponseT:
        path = _bbs_path(category, bbs_id, comment_id)
        return self._client.get(path, params=params)

    def create_bbs(self, category: str, **fields: RequestValue) -> ResponseT:
        return self._client.post(f"bbs/{category}.json", data=fields)

    def create_bbs_from(self, category: str, post: BbsPostInput) -> ResponseT:
        return self.create_bbs(category, **post.to_request_data())

    def update_bbs(self, category: str, bbs_id: int | str, **fields: RequestValue) -> ResponseT:
        return self._client.put(f"bbs/{category}/{bbs_id}.json", data=fields)

    def update_bbs_from(
        self,
        category: str,
        bbs_id: int | str,
        post: BbsPostInput,
    ) -> ResponseT:
        return self.update_bbs(category, bbs_id, **post.to_request_data())

    def delete_bbs(self, category: str, bbs_ids: int | str | Sequence[int | str]) -> ResponseT:
        return self._client.delete(f"bbs/{category}/{_comma_join(bbs_ids)}.json")

    def create_bbs_comment(
        self,
        category: str,
        bbs_id: int | str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.post(f"bbs/{category}/{bbs_id}.json", data=fields)

    def create_bbs_comment_from(
        self,
        category: str,
        bbs_id: int | str,
        comment: BbsCommentInput,
    ) -> ResponseT:
        return self.create_bbs_comment(category, bbs_id, **comment.to_request_data())

    def update_bbs_comment(
        self,
        category: str,
        bbs_id: int | str,
        comment_id: str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.put(f"bbs/{category}/{bbs_id}/{comment_id}.json", data=fields)

    def update_bbs_comment_from(
        self,
        category: str,
        bbs_id: int | str,
        comment_id: str,
        comment: BbsCommentInput,
    ) -> ResponseT:
        return self.update_bbs_comment(category, bbs_id, comment_id, **comment.to_request_data())

    def delete_bbs_comment(
        self,
        category: str,
        bbs_id: int | str,
        comment_ids: str | Sequence[str],
    ) -> ResponseT:
        return self._client.delete(f"bbs/{category}/{bbs_id}/{_comma_join(comment_ids)}.json")

    def create_bbs_reply(
        self,
        category: str,
        bbs_id: int | str,
        comment_id: str,
        **fields: RequestValue,
    ) -> ResponseT:
        return self._client.post(f"bbs/{category}/{bbs_id}/{comment_id}.json", data=fields)

    def create_bbs_reply_from(
        self,
        category: str,
        bbs_id: int | str,
        comment_id: str,
        reply: BbsCommentInput,
    ) -> ResponseT:
        return self.create_bbs_reply(category, bbs_id, comment_id, **reply.to_request_data())

    def delete_bbs_reply(
        self,
        category: str,
        bbs_id: int | str,
        comment_id: str,
        addition_ids: str | Sequence[int | str],
    ) -> ResponseT:
        return self._client.delete(
            f"bbs/{category}/{bbs_id}/{comment_id}/{_comma_join(addition_ids)}.json"
        )

    def recommend_bbs(self, *, bbs_id: int | str, comment_id: str | None = None) -> ResponseT:
        return self._client.put(
            "bbs/recommandation.json",
            data={"bbs_id": bbs_id, "comment_id": comment_id},
        )

    def prepare_upload(self, *, name: str, mime_type: str, size: int) -> ResponseT:
        return self._client.get(
            "upload.json",
            params={"name": name, "mimeType": mime_type, "size": size},
        )

    def complete_upload(self, uuid: str) -> ResponseT:
        return self._client.post("upload.json", data={"uuid": uuid})

    def notifications(self, *, section_id: str | None = None) -> ResponseT:
        return self._client.get("notifications.json", params={"section_id": section_id})

    def mark_notifications_read(self) -> ResponseT:
        return self._client.put("notifications.json")


def _comma_join(values: str | int | Sequence[str | int]) -> str:
    if isinstance(values, str | int):
        return str(values)
    return ",".join(str(value) for value in values)


def _with_section(section_id: str, params: Mapping[str, RequestValue]) -> RequestData:
    return {"section_id": section_id, **params}


def _nested_path(resource: str, first: str | None, second: str | None) -> str:
    if first is None:
        return f"{resource}.json"
    if second is None:
        return f"{resource}/{first}.json"
    return f"{resource}/{first}/{second}.json"


def _report_path(resource: str, account: str | None, account_id: str | None) -> str:
    if account is None:
        return f"{resource}.json"
    if account_id is None:
        return f"{resource}/{account}.json"
    return f"{resource}/{account}/{account_id}.json"


def _bbs_path(category: str | None, bbs_id: int | str | None, comment_id: str | None) -> str:
    if category is None:
        return "bbs.json"
    if bbs_id is None:
        return f"bbs/{category}.json"
    if comment_id is None:
        return f"bbs/{category}/{bbs_id}.json"
    return f"bbs/{category}/{bbs_id}/{comment_id}.json"
