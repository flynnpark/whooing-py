from __future__ import annotations

from enum import IntEnum
from typing import Generic, Literal, TypeAlias, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

T = TypeVar("T")


class WhooingModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApiCode(IntEnum):
    OK = 200
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    API_LIMIT_EXCEEDED = 402
    AUTH_EXPIRED = 405
    INTERNAL_ERROR = 500


class ErrorParameters(WhooingModel):
    field: str | None = None
    parameter: str | None = None
    reason: str | None = None
    expected: str | int | float | bool | None = None
    actual: str | int | float | bool | None = None


def _normalize_error_parameters(value: object) -> object:
    if value is None:
        return {}
    if isinstance(value, list) and len(value) == 0:
        return {}
    return value


class WhooingEnvelope(WhooingModel):
    code: ApiCode | int | None = None
    message: str = ""
    error_parameters: ErrorParameters = Field(default_factory=ErrorParameters)
    rest_of_api: int | None = None

    @field_validator("error_parameters", mode="before")
    @classmethod
    def normalize_error_parameters(cls, value: object) -> object:
        return _normalize_error_parameters(value)


class WhooingAPIResponse(WhooingModel, Generic[T]):
    code: ApiCode | int | None = None
    message: str = ""
    error_parameters: ErrorParameters = Field(default_factory=ErrorParameters)
    rest_of_api: int | None = None
    results: T | None = None

    @field_validator("error_parameters", mode="before")
    @classmethod
    def normalize_error_parameters(cls, value: object) -> object:
        return _normalize_error_parameters(value)


class WhooingSuccessResponse(WhooingEnvelope, Generic[T]):
    code: Literal[ApiCode.OK, 200] = ApiCode.OK
    results: T


class WhooingNoContentResponse(WhooingEnvelope):
    code: Literal[ApiCode.NO_CONTENT, 204] = ApiCode.NO_CONTENT
    results: None = None

    @model_validator(mode="after")
    def validate_no_content_message(self) -> WhooingNoContentResponse:
        if self.message and self.message.lower() not in {"", "no content"}:
            return self
        return self


class WhooingErrorResponse(WhooingEnvelope):
    code: Literal[
        ApiCode.BAD_REQUEST,
        ApiCode.UNAUTHORIZED,
        ApiCode.API_LIMIT_EXCEEDED,
        ApiCode.AUTH_EXPIRED,
        ApiCode.INTERNAL_ERROR,
        400,
        401,
        402,
        405,
        500,
    ]
    results: None = None


class OAuthErrorResponse(WhooingModel):
    error: str
    error_description: str | None = None


class OAuth2TokenResponse(WhooingModel):
    access_token: str
    token_type: str
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None


class OAuth2MetadataResponse(WhooingModel):
    issuer: str | None = None
    authorization_endpoint: str
    token_endpoint: str
    revocation_endpoint: str | None = None
    response_types_supported: list[str] | None = None
    grant_types_supported: list[str] | None = None
    code_challenge_methods_supported: list[str] | None = None
    scopes_supported: list[str] | None = None


class OAuth1RequestTokenResponse(WhooingModel):
    token: str


class OAuth1AccessTokenResponse(WhooingModel):
    token: str
    token_secret: str
    user_id: int | None = None


class HttpRateLimitResponse(WhooingModel):
    status_code: Literal[429] = 429
    retry_after: float | None = None


WhooingStrictResponse: TypeAlias = (
    WhooingSuccessResponse[T] | WhooingNoContentResponse | WhooingErrorResponse
)


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


UserResponse = WhooingAPIResponse[User]
UserLogsResponse = WhooingAPIResponse[list[UserLog]]
UserPointLogsResponse = WhooingAPIResponse[list[UserPointLog]]
SectionResponse = WhooingAPIResponse[Section]
SectionsResponse = WhooingAPIResponse[list[Section]]
AccountsResponse = WhooingAPIResponse[Accounts]
AccountResponse = WhooingAPIResponse[Account]
EntriesResponse = WhooingAPIResponse[list[Entry]]
EntryResponse = WhooingAPIResponse[Entry]
EntryAnalysisResponse = WhooingAPIResponse[list[EntryAnalysis]]
FrequentItemsResponse = WhooingAPIResponse[list[FrequentItem]]
MonthlyItemsResponse = WhooingAPIResponse[list[MonthlyItem]]
BudgetsResponse = WhooingAPIResponse[list[Budget]]
BudgetGoalResponse = WhooingAPIResponse[BudgetGoal]
CapitalGoalResponse = WhooingAPIResponse[CapitalGoal]
BillsResponse = WhooingAPIResponse[list[Bill]]
CheckcardsResponse = WhooingAPIResponse[list[Checkcard]]
InOutResponse = WhooingAPIResponse[list[InOut]]
CalendarResponse = WhooingAPIResponse[list[CalendarItem]]
ReportResponse = WhooingAPIResponse[list[Report]]
ReportSummaryResponse = WhooingAPIResponse[ReportSummary]
CustomReportRowsResponse = WhooingAPIResponse[list[CustomReportRow]]
PostItsResponse = WhooingAPIResponse[list[PostIt]]
PostItResponse = WhooingAPIResponse[PostIt]
MessagesResponse = WhooingAPIResponse[list[Message]]
BbsPostsResponse = WhooingAPIResponse[list[BbsPost]]
BbsPostResponse = WhooingAPIResponse[BbsPost]
BbsCommentsResponse = WhooingAPIResponse[list[BbsComment]]
UploadInfoResponse = WhooingAPIResponse[UploadInfo]
NotificationsResponse = WhooingAPIResponse[list[Notification]]
