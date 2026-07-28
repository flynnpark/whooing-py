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
    username: str | None = None
    country: str | None = None
    language: str | None = None
    timezone: str | None = None
    currency: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            optional={
                "username": self.username,
                "country": self.country,
                "language": self.language,
                "timezone": self.timezone,
                "currency": self.currency,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class SectionInput:
    title: str
    currency: str
    memo: str | None = None
    skin_id: int | str | None = None
    decimal_places: int | None = None
    date_format: str | None = None
    start_year: int | None = None
    template_id: int | str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"title": self.title, "currency": self.currency},
            optional={
                "memo": self.memo,
                "skin_id": self.skin_id,
                "decimal_places": self.decimal_places,
                "date_format": self.date_format,
                "start_year": self.start_year,
                "template_id": self.template_id,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class AccountInput:
    account_type: Literal["group", "account"]
    open_date: int | str
    close_date: int | str
    title: str | None = None
    memo: str | None = None
    category: str | None = None
    opt_use_date: int | str | None = None
    opt_pay_date: int | None = None
    opt_pay_account_id: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "type": self.account_type,
                "open_date": self.open_date,
                "close_date": self.close_date,
            },
            optional={
                "title": self.title,
                "memo": self.memo,
                "category": self.category,
                "opt_use_date": self.opt_use_date,
                "opt_pay_date": self.opt_pay_date,
                "opt_pay_account_id": self.opt_pay_account_id,
            },
            extra_fields=self.extra_fields,
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
    base_ym: int | str
    goal_ym: int | str
    goal_money: int | float
    base_money: int | float | None = None
    base_income: int | float | None = None
    base_expenses: int | float | None = None
    each_months: str | None = None
    split_type: Literal["auto", "equal", "manual"] | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "base_ym": self.base_ym,
                "goal_ym": self.goal_ym,
                "goal_money": self.goal_money,
            },
            optional={
                "base_money": self.base_money,
                "base_income": self.base_income,
                "base_expenses": self.base_expenses,
                "each_months": self.each_months,
                "split_type": self.split_type,
            },
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
    page: str
    contents: str
    everywhere: Literal["y", "n"] | None = None
    color: str | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "section_id": self.section_id,
                "page": self.page,
                "contents": self.contents,
            },
            optional={"everywhere": self.everywhere, "color": self.color},
        )


@dataclass(frozen=True, slots=True)
class FrequentItemInput:
    section_id: str
    item: str
    left_account: AccountType
    right_account: AccountType
    money: int | float | None = None
    left_account_id: str | None = None
    right_account_id: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "section_id": self.section_id,
                "item": self.item,
                "l_account": self.left_account,
                "r_account": self.right_account,
            },
            optional={
                "money": self.money,
                "l_account_id": self.left_account_id,
                "r_account_id": self.right_account_id,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class MonthlyItemInput:
    section_id: str
    item: str
    pay_date: int
    money: int | float | None = None
    left_account: AccountType | None = None
    left_account_id: str | None = None
    right_account: AccountType | None = None
    right_account_id: str | None = None
    skip_holiday: Literal["none", "before", "after"] | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"section_id": self.section_id, "item": self.item, "pay_date": self.pay_date},
            optional={
                "money": self.money,
                "l_account": self.left_account,
                "l_account_id": self.left_account_id,
                "r_account": self.right_account,
                "r_account_id": self.right_account_id,
                "skip_holiday": self.skip_holiday,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class MessageInput:
    opponent_user_ids: str | list[int | str]
    message: str
    attachment_ids: str | None = None

    def to_request_data(self) -> RequestData:
        opponent_user_ids = (
            self.opponent_user_ids
            if isinstance(self.opponent_user_ids, str)
            else ",".join(str(user_id) for user_id in self.opponent_user_ids)
        )
        return _request_data(
            required={"opponent_user_ids": opponent_user_ids, "message": self.message},
            optional={"attachment_ids": self.attachment_ids},
        )


@dataclass(frozen=True, slots=True)
class BbsPostInput:
    subject: str
    contents: str
    group: str | None = None
    language: str | None = None
    attachment_ids: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"subject": self.subject, "contents": self.contents},
            optional={
                "group": self.group,
                "language": self.language,
                "attachment_ids": self.attachment_ids,
            },
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class BbsCommentInput:
    contents: str
    attachment_ids: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={"contents": self.contents},
            optional={"attachment_ids": self.attachment_ids},
            extra_fields=self.extra_fields,
        )


@dataclass(frozen=True, slots=True)
class EntryInput:
    left_account: AccountType
    left_account_id: str
    right_account: AccountType
    right_account_id: str
    money: int | float
    entry_date: int | str | None = None
    item: str | None = None
    memo: str | None = None
    attachment_ids: str | None = None

    def to_request_data(self) -> RequestData:
        return _request_data(
            required={
                "l_account": self.left_account,
                "l_account_id": self.left_account_id,
                "r_account": self.right_account,
                "r_account_id": self.right_account_id,
                "money": self.money,
            },
            optional={
                "entry_date": self.entry_date,
                "item": self.item,
                "memo": self.memo,
                "attachment_ids": self.attachment_ids,
            },
        )

    def to_json_object(self) -> JsonObject:
        return {key: _json_value(value) for key, value in self.to_request_data().items()}


def _json_value(value: RequestValue) -> JsonValue:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Sequence):
        return [_json_value(item) for item in value]
    return value
