from __future__ import annotations

from whooing.pydantic_models import (
    AccountsResponse,
    ApiCode,
    EntriesResponse,
    ErrorParameters,
    NotificationsResponse,
    OAuth1AccessTokenResponse,
    OAuth1RequestTokenResponse,
    OAuth2MetadataResponse,
    OAuth2TokenResponse,
    OAuthErrorResponse,
    SectionResponse,
    SectionsResponse,
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
