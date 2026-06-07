from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from whooing.types import JsonObject, RequestData, RequestValue

AccountType = Literal["assets", "liabilities", "capital", "expenses", "income"]


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
