from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from whooing.types import JsonObject, RequestData, RequestValue

AccountType = Literal["assets", "liabilities", "capital", "expenses", "income"]


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
