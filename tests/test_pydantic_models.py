from __future__ import annotations

from whooing.pydantic_models import (
    AccountsResponse,
    EntriesResponse,
    NotificationsResponse,
    SectionResponse,
    SectionsResponse,
    UserResponse,
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
            "results": [{"notification_id": 1, "title": "알림"}],
        }
    )

    entries = entries_response.parse(EntriesResponse)
    notifications = notifications_response.parse(NotificationsResponse)

    assert entries.results is not None
    assert entries.results[0].item == "커피"
    assert notifications.results is not None
    assert notifications.results[0].title == "알림"
