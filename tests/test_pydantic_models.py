from __future__ import annotations

from whooing.pydantic_models import (
    Account,
    AccountExistenceResponse,
    AccountGroupValue,
    AccountsByTypeResponse,
    AccountsResponse,
    ApiCode,
    BbsPostResponse,
    BbsPostsResponse,
    BudgetReportResponse,
    CalendarResponse,
    CapitalGoalsResponse,
    CustomReportRowsResultResponse,
    EntriesListResponse,
    EntriesResponse,
    Entry,
    EntryChangeResponse,
    EntryFlowResponse,
    EntryNameAmountResponse,
    ErrorParameters,
    FrequentItemsSlotsResponse,
    InOutAccountResponse,
    InOutResponse,
    MonthlyItemsResponse,
    NotificationsResponse,
    OAuth1AccessTokenResponse,
    OAuth1RequestTokenResponse,
    OAuth2MetadataResponse,
    OAuth2TokenResponse,
    OAuthErrorResponse,
    ReportResponse,
    ReportSummaryResponse,
    SectionResponse,
    SectionsResponse,
    UnreadMessagesResponse,
    UploadInfoResponse,
    User,
    UserResponse,
    WhooingErrorResponse,
    WhooingNoContentResponse,
    WhooingSuccessResponse,
)
from whooing.response import parse_api_response


def test_user_response_model_parses_documented_shape() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "user_id": 4,
                "username": "Helloman",
                "timezone": "Asia/Seoul",
                "currency": "KRW",
            },
        }
    )

    parsed = response.parse(UserResponse)

    assert parsed.results is not None
    assert parsed.results.username == "Helloman"


def test_response_model_normalizes_empty_error_parameters_array() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": [],
            "rest_of_api": 4988,
            "results": {
                "user_id": 4,
                "username": "Helloman",
                "timezone": "Asia/Seoul",
                "currency": "KRW",
            },
        }
    )

    parsed = response.parse(UserResponse)

    assert isinstance(parsed.error_parameters, ErrorParameters)
    assert parsed.error_parameters.field is None


def test_section_models_parse_list_and_single_result() -> None:
    list_response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [{"section_id": "s123", "title": "유동성 자산", "currency": "KRW"}],
        }
    )
    single_response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {"section_id": "s123", "title": "유동성 자산", "currency": "KRW"},
        }
    )

    parsed_list = list_response.parse(SectionsResponse)
    parsed_single = single_response.parse(SectionResponse)

    assert parsed_list.results is not None
    assert parsed_list.results[0].section_id == "s123"
    assert parsed_single.results is not None
    assert parsed_single.results.title == "유동성 자산"


def test_accounts_response_model_parses_account_groups() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "assets": [{"account_id": "x1", "type": "account", "title": "현금"}],
                "liabilities": [],
                "capital": [],
                "income": [],
                "expenses": [],
            },
        }
    )

    parsed = response.parse(AccountsResponse)

    assert parsed.results is not None
    assert parsed.results.assets[0].title == "현금"


def test_domain_type_aliases_are_exported_and_described_in_schema() -> None:
    account_schema = Account.model_json_schema()
    entry_schema = Entry.model_json_schema()

    assert AccountGroupValue is not None
    assert account_schema["properties"]["open_date"]["title"] == "개설일"
    assert entry_schema["properties"]["money"]["title"] == "금액"
    assert "거래 금액" in entry_schema["properties"]["money"]["description"]


def test_entries_and_notifications_models_allow_extra_api_fields() -> None:
    entries_response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [
                {
                    "entry_id": 1,
                    "entry_date": 20260610,
                    "item": "커피",
                    "money": 5000,
                    "unknown_future_field": "kept",
                }
            ],
        }
    )
    notifications_response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "account": 0,
                "messages": 0,
                "messages_count": 0,
                "newReleases": 0,
                "notification": {
                    "badgeCount": 1,
                    "lastTimestamp": 1781280000,
                    "rows": [{"noti_id": 1, "contents": "알림", "timestamp": 1781280000}],
                },
                "outside": 0,
                "payment": 0,
            },
        }
    )

    entries = entries_response.parse(EntriesResponse)
    notifications = notifications_response.parse(NotificationsResponse)

    assert entries.results is not None
    assert entries.results[0].item == "커피"
    assert notifications.results is not None
    assert notifications.results.notification is not None
    assert notifications.results.notification.rows[0].contents == "알림"


def test_actual_report_account_and_entry_shapes_parse() -> None:
    accounts = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [
                {
                    "account_id": "x1",
                    "type": "assets",
                    "title": "현금",
                    "open_date": 20260101,
                    "close_date": None,
                    "opt_1": "sample",
                    "opt_2": None,
                    "opt_3": None,
                    "opt_4": None,
                }
            ],
        }
    ).parse(AccountsByTypeResponse)
    existence = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "count": 3,
                "minDate": 20260101,
                "maxDate": 20260612,
                "balance": 1000,
                "last_one": "n",
                "clients": ["sample"],
            },
        }
    ).parse(AccountExistenceResponse)
    entries = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "reports": [{"title": "sample"}],
                "rows": [
                    {
                        "entry_id": "e1",
                        "entry_date": 20260612,
                        "item": "테스트",
                        "money": 1000,
                        "total": "1,000",
                        "attachments": [],
                    }
                ],
            },
        }
    ).parse(EntriesListResponse)

    assert accounts.results is not None
    assert accounts.results[0].opt_1 == "sample"
    assert existence.results is not None
    assert existence.results.min_date == 20260101
    assert entries.results is not None
    assert entries.results.rows[0].total == "1,000"


def test_actual_report_analysis_budget_and_goal_shapes_parse() -> None:
    changes = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "aggregate": {"in": 1000, "out": 500},
                "rows_type": "daily",
                "rows": [{"date": 20260612, "money": 500}],
            },
        }
    ).parse(EntryChangeResponse)
    names = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [{"name": "거래처", "money": 1000}],
        }
    ).parse(EntryNameAmountResponse)
    budget = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "aggregate": {"budget": 2000, "money": 1000, "remains": 1000},
                "max": 2000,
                "rows_type": "accounts",
                "rows": [
                    {
                        "title": "식비",
                        "budget": 2000,
                        "money": 1000,
                        "remains": 1000,
                        "accounts": [{"account_id": "x1", "budget": 2000, "money": 1000}],
                    }
                ],
            },
        }
    ).parse(BudgetReportResponse)
    capital_goals = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [{"date": 202606, "money": None}],
        }
    ).parse(CapitalGoalsResponse)

    assert changes.results is not None
    assert changes.results.aggregate is not None
    assert changes.results.aggregate.in_ == 1000
    assert names.results is not None
    assert names.results[0].name == "거래처"
    assert budget.results is not None
    assert budget.results.rows[0].accounts[0].account_id == "x1"
    assert capital_goals.results is not None
    assert capital_goals.results[0].money is None


def test_actual_report_flow_report_and_calendar_shapes_parse() -> None:
    flow = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "assets": {
                    "total": {"from": 1000, "to": 1200, "margin": 200},
                    "accounts": [{"account_id": "x1", "from": 1000, "to": 1200, "margin": 200}],
                },
                "liabilities": {"total": {"from": 0, "to": 0, "margin": 0}, "accounts": []},
                "capital": {"total": {"from": 0, "to": 0, "margin": 0}, "accounts": []},
                "income": {"total": {"from": 0, "to": 0, "margin": 0}, "accounts": []},
                "expenses": {"total": {"from": 0, "to": 0, "margin": 0}, "accounts": []},
            },
        }
    ).parse(EntryFlowResponse)
    report = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "income": {
                    "total": 3000,
                    "accounts": {"x1": 3000},
                    "total_steady": 0,
                    "total_floating": 3000,
                },
                "expenses": {
                    "total": 1000,
                    "accounts": {"x2": 1000},
                    "total_steady": 0,
                    "total_floating": 1000,
                },
                "net_income": {"total": 2000},
            },
        }
    ).parse(ReportResponse)
    summary = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {"assets": {"total": 1200, "accounts": {"x1": 1200}}},
        }
    ).parse(ReportSummaryResponse)
    calendar = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "aggregate": {"count": 1, "income": 0, "expenses": 1000, "etc": 0},
                "rows_type": "calendar",
                "rows": {
                    "202606": [
                        {
                            "day": 1,
                            "date": 20260601,
                            "count": 1,
                            "income": 0,
                            "expenses": 1000,
                            "etc": 0,
                            "is_holiday": False,
                            "label": "",
                        }
                    ]
                },
            },
        }
    ).parse(CalendarResponse)

    assert flow.results is not None
    assert flow.results.assets is not None
    assert flow.results.assets.total is not None
    assert flow.results.assets.total.from_ == 1000
    assert report.results is not None
    assert report.results.income is not None
    assert report.results.income.accounts["x1"] == 3000
    assert summary.results is not None
    assert summary.results.assets is not None
    assert calendar.results is not None
    assert isinstance(calendar.results.rows["202606"], list)


def test_actual_report_extras_and_notification_shapes_parse() -> None:
    frequent_items = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "slot1": [{"item_id": 1, "item": "커피", "money": 5000}],
                "slot2": [],
                "slot3": [],
                "slot4": [],
                "slot5": [],
            },
        }
    ).parse(FrequentItemsSlotsResponse)
    monthly_items = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "count": 1,
                "slot1": [
                    {
                        "item_id": 1,
                        "item": "구독",
                        "due_date": 20260615,
                        "paid_date": None,
                        "pay_date": 15,
                        "skip_holiday": "n",
                    }
                ],
            },
        }
    ).parse(MonthlyItemsResponse)
    in_out = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "accounts": [
                    {"account_id": "x1", "balance": 1000, "in": 300, "out": 100, "margin": 200}
                ],
                "total": {"balance": 1000, "in": 300, "out": 100, "margin": 200},
            },
        }
    ).parse(InOutAccountResponse)
    upload = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "url": "https://example.com/upload",
                "file_info": {
                    "uuid": "file-uuid",
                    "name": "receipt.png",
                    "size": 10,
                    "mimeType": "image/png",
                },
            },
        }
    ).parse(UploadInfoResponse)

    assert frequent_items.results is not None
    assert frequent_items.results.slot1[0].item == "커피"
    assert monthly_items.results is not None
    assert monthly_items.results.slot1[0].due_date == 20260615
    assert in_out.results is not None
    assert in_out.results.total is not None
    assert in_out.results.total.in_ == 300
    assert upload.results is not None
    assert upload.results.file_info is not None
    assert upload.results.file_info.mime_type == "image/png"


def test_actual_report_in_out_overview_shape_parse() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": {
                "assets": {
                    "total": {"in": 300, "out": 100, "margin": 200},
                    "accounts": [{"account_id": "x1", "in": 300, "out": 100, "margin": 200}],
                },
                "liabilities": {},
            },
        }
    ).parse(InOutResponse)

    assert response.results is not None
    assert response.results.assets is not None


def test_actual_report_bbs_shape_accepts_counted_comments() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [
                {
                    "bbs_id": 1,
                    "category": "notice",
                    "subject": "공지",
                    "comments": 2,
                    "contents": "내용",
                    "group": "bbs",
                    "hits": 10,
                    "is_attachment": False,
                    "language": "ko",
                    "latest": 1781280000,
                    "notice": True,
                    "recommandation": 0,
                    "shorturl": "abc",
                    "thumb_path": "",
                    "timestamp": 1781280000,
                    "updated_at": 1781280000,
                    "writer": {"user_id": 1, "username": "tester"},
                }
            ],
        }
    ).parse(BbsPostsResponse)

    assert response.results is not None
    assert response.results[0].subject == "공지"
    assert response.results[0].comments == 2


def test_actual_report_unread_messages_and_empty_bbs_post_shapes_parse() -> None:
    unread = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": 0,
        }
    ).parse(UnreadMessagesResponse)
    empty_post = parse_api_response(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 4988,
            "results": [],
        }
    ).parse(BbsPostResponse)

    assert unread.results == 0
    assert empty_post.results == []


def test_report_custom_rows_result_uses_documented_non_envelope_shape() -> None:
    parsed = CustomReportRowsResultResponse.model_validate(
        {
            "status": "done",
            "rows": [
                {
                    "id": "12",
                    "report": "report_bs",
                    "title": "현금성 자산",
                    "plus": ["assets_x11"],
                    "minus": ["liabilities_total"],
                    "addminus": "x",
                    "money": 0,
                }
            ],
        }
    )

    assert parsed.status == "done"
    assert parsed.rows[0].plus == ["assets_x11"]


def test_strict_success_response_requires_results() -> None:
    parsed = WhooingSuccessResponse[User].model_validate(
        {
            "code": 200,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 10,
            "results": {"user_id": 1, "username": "flynn"},
        }
    )

    assert parsed.code == ApiCode.OK
    assert parsed.results.username == "flynn"


def test_no_content_response_models_204_without_results() -> None:
    parsed = WhooingNoContentResponse.model_validate(
        {
            "code": 204,
            "message": "",
            "error_parameters": {},
            "rest_of_api": 9,
        }
    )

    assert parsed.code == ApiCode.NO_CONTENT
    assert parsed.results is None


def test_error_response_models_documented_error_codes() -> None:
    parsed = WhooingErrorResponse.model_validate(
        {
            "code": 400,
            "message": "bad parameter",
            "error_parameters": {"field": "section_id", "reason": "required"},
            "rest_of_api": 8,
        }
    )

    assert parsed.code == ApiCode.BAD_REQUEST
    assert isinstance(parsed.error_parameters, ErrorParameters)
    assert parsed.error_parameters.field == "section_id"


def test_oauth_error_response_model() -> None:
    parsed = OAuthErrorResponse.model_validate(
        {"error": "invalid_grant", "error_description": "expired"}
    )

    assert parsed.error == "invalid_grant"
    assert parsed.error_description == "expired"


def test_oauth2_token_and_metadata_response_models() -> None:
    token = OAuth2TokenResponse.model_validate(
        {
            "access_token": "access",
            "token_type": "Bearer",
            "expires_in": 31536000,
            "refresh_token": "refresh",
            "scope": "read,write",
        }
    )
    metadata = OAuth2MetadataResponse.model_validate(
        {
            "authorization_endpoint": "https://whooing.com/oauth2/authorize",
            "token_endpoint": "https://whooing.com/oauth2/token",
            "revocation_endpoint": "https://whooing.com/oauth2/revoke",
            "code_challenge_methods_supported": ["S256"],
        }
    )

    assert token.token_type == "Bearer"
    assert metadata.code_challenge_methods_supported == ["S256"]


def test_oauth1_token_response_models() -> None:
    request_token = OAuth1RequestTokenResponse.model_validate({"token": "request-token"})
    access_token = OAuth1AccessTokenResponse.model_validate(
        {"token": "access-token", "token_secret": "secret", "user_id": 1}
    )

    assert request_token.token == "request-token"
    assert access_token.token_secret == "secret"
