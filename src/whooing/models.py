from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from whooing.types import JsonObject, RequestData, RequestValue

AccountType = Literal["assets", "liabilities", "capital", "expenses", "income"]


@dataclass(frozen=True, slots=True)
class UserInput:
    nickname: str | None = None
    language: str | None = None
    timezone: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        data: dict[str, RequestValue] = {}
        if self.nickname is not None:
            data["nickname"] = self.nickname
        if self.language is not None:
            data["language"] = self.language
        if self.timezone is not None:
            data["timezone"] = self.timezone
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


@dataclass(frozen=True, slots=True)
class SectionInput:
    title: str
    currency: str | None = None
    memo: str | None = None
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        data: dict[str, RequestValue] = {"title": self.title}
        if self.currency is not None:
            data["currency"] = self.currency
        if self.memo is not None:
            data["memo"] = self.memo
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


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
        data: dict[str, RequestValue] = {"title": self.title}
        if self.memo is not None:
            data["memo"] = self.memo
        if self.open_date is not None:
            data["open_date"] = self.open_date
        if self.close_date is not None:
            data["close_date"] = self.close_date
        if self.currency is not None:
            data["currency"] = self.currency
        if self.initial_money is not None:
            data["initial_money"] = self.initial_money
        if self.order is not None:
            data["order"] = self.order
        if self.group is not None:
            data["group"] = self.group
        return data


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
        data: dict[str, RequestValue] = {}
        if self.start_date is not None:
            data["start_date"] = self.start_date
        if self.end_date is not None:
            data["end_date"] = self.end_date
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


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
        data: dict[str, RequestValue] = {
            "section_id": self.section_id,
            "title": self.title,
            "contents": self.contents,
        }
        if self.position is not None:
            data["position"] = self.position
        if self.color is not None:
            data["color"] = self.color
        return data


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
        data: dict[str, RequestValue] = {
            "section_id": self.section_id,
            "item": self.item,
        }
        if self.money is not None:
            data["money"] = self.money
        if self.memo is not None:
            data["memo"] = self.memo
        if self.left_account is not None:
            data["l_account"] = self.left_account
        if self.left_account_id is not None:
            data["l_account_id"] = self.left_account_id
        if self.right_account is not None:
            data["r_account"] = self.right_account
        if self.right_account_id is not None:
            data["r_account_id"] = self.right_account_id
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


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
        data: dict[str, RequestValue] = {
            "section_id": self.section_id,
            "item": self.item,
        }
        if self.money is not None:
            data["money"] = self.money
        if self.memo is not None:
            data["memo"] = self.memo
        if self.start_date is not None:
            data["start_date"] = self.start_date
        if self.end_date is not None:
            data["end_date"] = self.end_date
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


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
        data: dict[str, RequestValue] = {"title": self.title, "contents": self.contents}
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


@dataclass(frozen=True, slots=True)
class BbsCommentInput:
    contents: str
    extra_fields: Mapping[str, RequestValue] | None = None

    def to_request_data(self) -> RequestData:
        data: dict[str, RequestValue] = {"contents": self.contents}
        if self.extra_fields is not None:
            data.update(self.extra_fields)
        return data


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
        data: dict[str, RequestValue] = {
            "entry_date": self.entry_date,
            "l_account": self.left_account,
            "l_account_id": self.left_account_id,
            "r_account": self.right_account,
            "r_account_id": self.right_account_id,
            "item": self.item,
            "money": self.money,
        }
        if self.memo is not None:
            data["memo"] = self.memo
        return data

    def to_json_object(self) -> JsonObject:
        data: JsonObject = {
            "entry_date": self.entry_date,
            "l_account": self.left_account,
            "l_account_id": self.left_account_id,
            "r_account": self.right_account,
            "r_account_id": self.right_account_id,
            "item": self.item,
            "money": self.money,
        }
        if self.memo is not None:
            data["memo"] = self.memo
        return data
