from __future__ import annotations

from whooing._pydantic_models.base import WhooingAPIResponse
from whooing._pydantic_models.resources import (
    Account,
    AccountExistence,
    Accounts,
    BbsComment,
    BbsPost,
    Bill,
    BillReport,
    Budget,
    BudgetGoal,
    BudgetReport,
    CalendarItem,
    CalendarReport,
    CapitalGoal,
    CapitalGoalRow,
    Checkcard,
    CustomReportRow,
    CustomReportRowsResult,
    Entry,
    EntryAnalysis,
    EntryChangeReport,
    EntryFlowReport,
    EntryList,
    EntryNameAmount,
    FrequentItem,
    FrequentItems,
    InOut,
    InOutDetail,
    InOutOverview,
    InOutReport,
    Message,
    MonthlyItem,
    MonthlyItems,
    Notification,
    Notifications,
    PostIt,
    Report,
    ReportResult,
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
AccountsByTypeResponse = WhooingAPIResponse[list[Account]]
AccountResponse = WhooingAPIResponse[Account]
AccountExistenceResponse = WhooingAPIResponse[AccountExistence]
EntriesListResponse = WhooingAPIResponse[EntryList]
EntriesResponse = WhooingAPIResponse[list[Entry]]
EntryResponse = WhooingAPIResponse[Entry]
EntryAnalysisResponse = WhooingAPIResponse[list[EntryAnalysis]]
EntryChangeResponse = WhooingAPIResponse[EntryChangeReport]
EntryFlowResponse = WhooingAPIResponse[EntryFlowReport]
EntryNameAmountResponse = WhooingAPIResponse[list[EntryNameAmount]]
FrequentItemsResponse = WhooingAPIResponse[list[FrequentItem]]
FrequentItemsSlotsResponse = WhooingAPIResponse[FrequentItems]
MonthlyItemsListResponse = WhooingAPIResponse[list[MonthlyItem]]
MonthlyItemsResponse = WhooingAPIResponse[MonthlyItems]
BudgetsResponse = WhooingAPIResponse[list[Budget]]
BudgetReportResponse = WhooingAPIResponse[BudgetReport]
BudgetGoalResponse = WhooingAPIResponse[BudgetGoal]
CapitalGoalResponse = WhooingAPIResponse[CapitalGoal]
CapitalGoalsResponse = WhooingAPIResponse[list[CapitalGoalRow]]
BillsListResponse = WhooingAPIResponse[list[Bill]]
BillsResponse = WhooingAPIResponse[BillReport]
CheckcardsListResponse = WhooingAPIResponse[list[Checkcard]]
CheckcardsResponse = WhooingAPIResponse[BillReport]
InOutListResponse = WhooingAPIResponse[list[InOut]]
InOutResponse = WhooingAPIResponse[InOutOverview]
InOutAccountResponse = WhooingAPIResponse[InOutReport]
InOutDetailResponse = WhooingAPIResponse[InOutDetail]
CalendarItemsResponse = WhooingAPIResponse[list[CalendarItem]]
CalendarResponse = WhooingAPIResponse[CalendarReport]
ReportsListResponse = WhooingAPIResponse[list[Report]]
ReportResponse = WhooingAPIResponse[ReportResult]
ReportSummaryResponse = WhooingAPIResponse[ReportSummary]
CustomReportRowsResponse = WhooingAPIResponse[list[CustomReportRow]]
CustomReportRowsResultResponse = CustomReportRowsResult
PostItsResponse = WhooingAPIResponse[list[PostIt]]
PostItResponse = WhooingAPIResponse[PostIt]
MessagesResponse = WhooingAPIResponse[list[Message]]
UnreadMessagesResponse = WhooingAPIResponse[int]
BbsPostsResponse = WhooingAPIResponse[list[BbsPost]]
BbsPostResponse = WhooingAPIResponse[BbsPost | list[BbsPost]]
BbsCommentsResponse = WhooingAPIResponse[list[BbsComment]]
UploadInfoResponse = WhooingAPIResponse[UploadInfo]
NotificationsListResponse = WhooingAPIResponse[list[Notification]]
NotificationsResponse = WhooingAPIResponse[Notifications]
