from __future__ import annotations

from whooing._pydantic_models.base import WhooingModel


class User(WhooingModel):
    user_id: int | None = None
    username: str | None = None
    last_ip: str | None = None
    last_login_timestamp: int | None = None
    created_timestamp: int | None = None
    modified_timestamp: int | None = None
    language: str | None = None
    level: str | int | None = None
    expire: int | None = None
    timezone: str | None = None
    currency: str | None = None
    country: str | None = None
    image_url: str | None = None
    mileage: int | float | None = None


class UserLog(WhooingModel):
    id: int | None = None
    contents: str | None = None
    datetime: int | None = None
    ip: str | None = None
    segment0: str | None = None
    segment1: str | None = None
    writer: str | None = None


class UserPointLog(WhooingModel):
    point_id: int | None = None
    datetime: int | None = None
    description: str | None = None
    point: int | float | None = None
    writer: str | None = None


class Section(WhooingModel):
    section_id: str | None = None
    title: str | None = None
    memo: str | None = None
    currency: str | None = None
    isolation: str | None = None
    total_assets: int | float | None = None
    total_liabilities: int | float | None = None
    skin_id: int | None = None
    decimal_places: int | None = None
    date_format: str | None = None
    webhook_token: str | None = None
    ui: dict[str, object] | None = None


class Account(WhooingModel):
    account_id: str | None = None
    type: str | None = None
    title: str | None = None
    memo: str | None = None
    open_date: int | str | None = None
    close_date: int | str | None = None
    category: str | None = None
    opt_use_date: str | int | None = None
    opt_pay_date: str | int | None = None
    opt_pay_account_id: str | None = None


class Accounts(WhooingModel):
    assets: list[Account] = []
    liabilities: list[Account] = []
    capital: list[Account] = []
    income: list[Account] = []
    expenses: list[Account] = []


class Entry(WhooingModel):
    entry_id: int | str | None = None
    entry_date: int | str | None = None
    l_account: str | None = None
    l_account_id: str | None = None
    r_account: str | None = None
    r_account_id: str | None = None
    item: str | None = None
    money: int | float | None = None
    memo: str | None = None
    timestamp: int | None = None


class EntryAnalysis(WhooingModel):
    account: str | None = None
    account_id: str | None = None
    item: str | None = None
    client: str | None = None
    money: int | float | None = None
    count: int | None = None
    entries: list[Entry] | None = None


class FrequentItem(WhooingModel):
    item_id: str | int | None = None
    section_id: str | None = None
    item: str | None = None
    money: int | float | None = None
    memo: str | None = None
    l_account: str | None = None
    l_account_id: str | None = None
    r_account: str | None = None
    r_account_id: str | None = None


class MonthlyItem(FrequentItem):
    start_date: int | str | None = None
    end_date: int | str | None = None


class Budget(WhooingModel):
    account_id: str | None = None
    target_ym: int | str | None = None
    money: int | float | None = None


class BudgetGoal(WhooingModel):
    section_id: str | None = None
    start_date: int | str | None = None
    end_date: int | str | None = None


class CapitalGoal(WhooingModel):
    section_id: str | None = None
    monthly_goals: dict[str, int | float] | None = None


class Bill(WhooingModel):
    account_id: str | None = None
    title: str | None = None
    money: int | float | None = None
    entry_date: int | str | None = None


class Checkcard(Bill):
    pass


class InOut(WhooingModel):
    account: str | None = None
    account_id: str | None = None
    in_money: int | float | None = None
    out_money: int | float | None = None
    balance: int | float | None = None


class CalendarItem(WhooingModel):
    entry_date: int | str | None = None
    entries: list[Entry] | None = None
    money: int | float | None = None


class Report(WhooingModel):
    account: str | None = None
    account_id: str | None = None
    money: int | float | None = None
    entries: list[Entry] | None = None


class ReportSummary(WhooingModel):
    account: str | None = None
    income: int | float | None = None
    expenses: int | float | None = None
    assets: int | float | None = None
    liabilities: int | float | None = None
    capital: int | float | None = None


class CustomReportRow(WhooingModel):
    row_id: str | int | None = None
    title: str | None = None
    account: str | None = None
    account_id: str | None = None


class PostIt(WhooingModel):
    post_it_id: int | str | None = None
    section_id: str | None = None
    title: str | None = None
    contents: str | None = None
    position: str | None = None
    color: str | None = None


class Message(WhooingModel):
    message_id: int | str | None = None
    opponent_user_id: int | str | None = None
    message: str | None = None
    contents: str | None = None
    datetime: int | None = None
    read: str | bool | None = None


class BbsPost(WhooingModel):
    bbs_id: int | str | None = None
    category: str | None = None
    title: str | None = None
    contents: str | None = None
    user_id: int | None = None
    datetime: int | None = None
    comments: list[BbsComment] | None = None


class BbsComment(WhooingModel):
    comment_id: str | int | None = None
    addition_id: str | int | None = None
    contents: str | None = None
    user_id: int | None = None
    datetime: int | None = None
    replies: list[BbsComment] | None = None


class UploadInfo(WhooingModel):
    uuid: str | None = None
    url: str | None = None
    fields: dict[str, object] | None = None


class Notification(WhooingModel):
    notification_id: int | str | None = None
    section_id: str | None = None
    title: str | None = None
    contents: str | None = None
    datetime: int | None = None
    read: str | bool | None = None
