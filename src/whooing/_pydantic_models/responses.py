from __future__ import annotations

from whooing._pydantic_models.base import WhooingAPIResponse
from whooing._pydantic_models.resources import (
    Account,
    Accounts,
    BbsComment,
    BbsPost,
    Bill,
    Budget,
    BudgetGoal,
    CalendarItem,
    CapitalGoal,
    Checkcard,
    CustomReportRow,
    Entry,
    EntryAnalysis,
    FrequentItem,
    InOut,
    Message,
    MonthlyItem,
    Notification,
    PostIt,
    Report,
    ReportSummary,
    Section,
    UploadInfo,
    User,
    UserLog,
    UserPointLog,
)

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
