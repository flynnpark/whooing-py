from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from whooing.types import JsonObject, JsonValue, RequestData, RequestValue

AccountType = Literal["assets", "liabilities", "capital", "expenses", "income"]


def _request_data(
    required: Mapping[str, RequestValue] | None = None,
    optional: Mapping[str, RequestValue] | None = None,
    extra_fields: Mapping[str, RequestValue] | None = None,
) -> RequestData:
    data: dict[str, RequestValue] = {}
    if required is not None:
        data.update(required)
    if optional is not None:
        data.update({key: value for key, value in optional.items() if value is not None})
    if extra_fields is not None:
        data.update(extra_fields)
    return data


@dataclass(frozen=True, slots=True)
class UserInput:
    nickname: str | None = None
    language: str | None = None
    timezone: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            optional={
                "nickname": self.nickname,
                "language": self.language,
                "timezone": self.timezone,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class SectionInput:
    title: str
    currency: str | None = None
    memo: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"title": self.title},
            optional={"currency": self.currency, "memo": self.memo},
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class AccountInput:
    title: str
    memo: str | None = None
    open_date: int | str | None = None
    close_date: int | str | None = None
    currency: str | None = None
    initial_money: int | float | None = None
    order: int | None = None
    group: str | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"title": self.title},
            optional={
                "memo": self.memo,
                "open_date": self.open_date,
                "close_date": self.close_date,
                "currency": self.currency,
                "initial_money": self.initial_money,
                "order": self.order,
                "group": self.group,
            },
        )


@dataclass(frozen=True, slots=True)
class BudgetInput:
    target_ym: int | str
    amounts_by_account_id: dict[str, int | float]

    def to_request_data(self) -> RequestData:
        data: dict[str, RequestValue] = {"target_ym": self.target_ym}
        data.update(self.amounts_by_account_id)
        return data


@dataclass(frozen=True, slots=True)
class BasicTotalBudgetInput:
    start_date: int | str
    end_date: int | str
    monthly_totals: dict[int, int | float]

    def to_request_data(self) -> RequestData:
        data: dict[str, RequestValue] = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        data.update({str(month): amount for month, amount in self.monthly_totals.items()})
        return data


@dataclass(frozen=True, slots=True)
class BudgetGoalInput:
    start_date: int | str | None = None
    end_date: int | str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            optional={"start_date": self.start_date, "end_date": self.end_date},
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class CapitalGoalInput:
    monthly_goals: Mapping[int | str, int | float]

    def to_request_data(self) -> RequestData:
        return {str(month): amount for month, amount in self.monthly_goals.items()}


@dataclass(frozen=True, slots=True)
class PostItInput:
    section_id: str
    title: str
    contents: str
    position: str | None = None
    color: str | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "section_id": self.section_id,
                "title": self.title,
                "contents": self.contents,
            },
            optional={"position": self.position, "color": self.color},
        )


@dataclass(frozen=True, slots=True)
class FrequentItemInput:
    section_id: str
    item: str
    money: int | float | None = None
    memo: str | None = None
    left_account: AccountType | None = None
    left_account_id: str | None = None
    right_account: AccountType | None = None
    right_account_id: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"section_id": self.section_id, "item": self.item},
            optional={
                "money": self.money,
                "memo": self.memo,
                "l_account": self.left_account,
                "l_account_id": self.left_account_id,
                "r_account": self.right_account,
                "r_account_id": self.right_account_id,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class MonthlyItemInput:
    section_id: str
    item: str
    money: int | float | None = None
    memo: str | None = None
    start_date: int | str | None = None
    end_date: int | str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"section_id": self.section_id, "item": self.item},
            optional={
                "money": self.money,
                "memo": self.memo,
                "start_date": self.start_date,
                "end_date": self.end_date,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class MessageInput:
    opponent_user_ids: str | list[int | str]
    message: str

    def to_request_data(self) -> RequestData:
        opponent_user_ids = (
            self.opponent_user_ids
            if isinstance(self.opponent_user_ids, str)
            else ",".join(str(user_id) for user_id in self.opponent_user_ids)
        )
        return {"opponent_user_ids": opponent_user_ids, "message": self.message}


@dataclass(frozen=True, slots=True)
class BbsPostInput:
    title: str
    contents: str
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"title": self.title, "contents": self.contents},
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class BbsCommentInput:
    contents: str
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(required={"contents": self.contents}, extra_fields=self.extra_fields)


@dataclass(frozen=True, slots=True)
class EntryInput:
    entry_date: int | str
    left_account: AccountType
    left_account_id: str
    right_account: AccountType
    right_account_id: str
    item: str
    money: int | float
    memo: str | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "entry_date": self.entry_date,
                "l_account": self.left_account,
                "l_account_id": self.left_account_id,
                "r_account": self.right_account,
                "r_account_id": self.right_account_id,
                "item": self.item,
                "money": self.money,
            },
            optional={"memo": self.memo},
        )

    def to_json_object(self) -> JsonObject:
        return {key: _json_value(value) for key, value in self.to_request_data().items()}


def _json_value(value: RequestValue) -> JsonValue:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Sequence):
        return [_json_value(item) for item in value]
    return value
