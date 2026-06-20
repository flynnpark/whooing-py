from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from whooing.auth import OAuth1RequestToken, OAuth2Token
from whooing.cli import app
from whooing.types import JsonObject, RequestData

runner = CliRunner()


def test_oauth2_url_command_outputs_pkce_payload() -> None:
    result = runner.invoke(
        app,
        [
            "auth",
            "oauth2-url",
            "--client-id",
            "app",
            "--redirect-uri",
            "http://localhost/callback",
            "--scope",
            "read",
            "--scope",
            "write",
            "--state",
            "state",
        ]
    )

    payload = cast(JsonObject, json.loads(result.stdout))
    authorization_url = urlparse(str(payload["authorization_url"]))
    query = parse_qs(authorization_url.query)

    assert result.exit_code == 0
    assert query["client_id"] == ["app"]
    assert query["redirect_uri"] == ["http://localhost/callback"]
    assert query["scope"] == ["read,write"]
    assert query["state"] == ["state"]
    assert query["code_challenge"] == [payload["code_challenge"]]
    assert payload["code_challenge_method"] == "S256"


def test_version_option_outputs_package_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == "whooing-py 0.1.0\n"


def test_help_exposes_resource_command_groups() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    for command in [
        "user",
        "sections",
        "accounts",
        "entries",
        "budgets",
        "reports",
        "extras",
    ]:
        assert command in result.stdout


def test_profile_commands_store_and_mask_credentials(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"

    set_result = runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "--profile",
            "work",
            "profile",
            "set",
            "--api-key",
            "abcd1234secret",
        ],
    )
    show_result = runner.invoke(
        app,
        ["--config", str(config_path), "--profile", "work", "profile", "show"],
    )
    list_result = runner.invoke(app, ["--config", str(config_path), "profile", "list"])

    assert set_result.exit_code == 0
    assert show_result.exit_code == 0
    assert list_result.exit_code == 0
    assert json.loads(show_result.stdout)["api_key"] == "abcd...cret"
    assert json.loads(list_result.stdout) == {"profiles": ["work"]}


def test_profile_list_supports_table_output(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "--profile",
            "work",
            "profile",
            "set",
            "--api-key",
            "secret",
        ],
    )

    result = runner.invoke(
        app,
        ["--config", str(config_path), "--output", "table", "profile", "list"],
    )

    assert result.exit_code == 0
    assert "profiles" in result.stdout
    assert "work" in result.stdout


def test_exchange_code_command_outputs_token(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeOAuth2TokenClient:
        def __init__(self, *, token_endpoint: str = "", revoke_endpoint: str = "") -> None:
            self.token_endpoint = token_endpoint
            self.revoke_endpoint = revoke_endpoint

        def __enter__(self) -> FakeOAuth2TokenClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def exchange_code(
            self,
            *,
            client_id: str,
            code: str,
            redirect_uri: str,
            code_verifier: str | None = None,
        ) -> OAuth2Token:
            assert self.token_endpoint == "https://token.example"
            assert client_id == "app"
            assert code == "code"
            assert redirect_uri == "http://localhost/callback"
            assert code_verifier == "verifier"
            return OAuth2Token(
                access_token="access",
                token_type="Bearer",
                expires_in=3600,
                refresh_token="refresh",
                scope="read",
                raw={"access_token": "access"},
            )

    monkeypatch.setattr("whooing.cli.OAuth2TokenClient", FakeOAuth2TokenClient)

    result = runner.invoke(
        app,
        [
            "auth",
            "exchange-code",
            "--client-id",
            "app",
            "--code",
            "code",
            "--redirect-uri",
            "http://localhost/callback",
            "--code-verifier",
            "verifier",
            "--token-endpoint",
            "https://token.example",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["access_token"] == "access"


def test_oauth1_request_token_command_outputs_authorization_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeAppAuthClient:
        def __init__(self, *, base_url: str = "") -> None:
            self.base_url = base_url

        def __enter__(self) -> FakeAppAuthClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def request_token(
            self,
            *,
            app_id: str,
            app_secret: str,
            callback_uri: str | None = None,
        ) -> OAuth1RequestToken:
            assert self.base_url == "https://app-auth.example/"
            assert app_id == "app"
            assert app_secret == "secret"
            assert callback_uri == "http://localhost/callback"
            return OAuth1RequestToken(token="request-token", raw={"token": "request-token"})

        def build_authorization_url(
            self,
            *,
            token: str,
            callback_uri: str | None = None,
            no_register: bool = False,
        ) -> str:
            assert token == "request-token"
            assert callback_uri is None
            assert no_register is False
            return "https://authorize.example?token=request-token"

    monkeypatch.setattr("whooing.cli.AppAuthClient", FakeAppAuthClient)

    result = runner.invoke(
        app,
        [
            "auth",
            "oauth1-request-token",
            "--app-id",
            "app",
            "--app-secret",
            "secret",
            "--callback-uri",
            "http://localhost/callback",
            "--base-url",
            "https://app-auth.example/",
        ],
    )

    payload = json.loads(result.stdout)

    assert result.exit_code == 0
    assert payload["token"] == "request-token"
    assert payload["authorization_url"] == "https://authorize.example?token=request-token"


def test_api_request_command_uses_auth_and_parses_pairs(monkeypatch: pytest.MonkeyPatch) -> None:
    @dataclass(frozen=True, slots=True)
    class FakeResponse:
        raw: JsonObject

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert base_url == "https://api.example/"
            assert api_key == "secret"
            assert access_token is None

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def request(
            self,
            method: str,
            path: str,
            *,
            params: RequestData | None = None,
            data: RequestData | None = None,
        ) -> FakeResponse:
            assert method == "GET"
            assert path == "sections.json"
            assert params == {"limit": 10}
            assert data is None
            return FakeResponse(raw={"code": 200, "results": [{"section_id": "s1"}]})

    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(
        app,
        [
            "--api-key",
            "secret",
            "--base-url",
            "https://api.example/",
            "api",
            "request",
            "GET",
            "sections.json",
            "--param",
            "limit=10",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout)["results"] == [{"section_id": "s1"}]


def test_api_request_validates_common_response_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @dataclass(frozen=True, slots=True)
    class FakeResponse:
        raw: JsonObject

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert base_url == "https://whooing.com/api/"
            assert api_key == "secret"
            assert access_token is None

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def request(
            self,
            method: str,
            path: str,
            *,
            params: RequestData | None = None,
            data: RequestData | None = None,
        ) -> FakeResponse:
            assert method == "GET"
            assert path == "sections.json"
            assert params is None
            assert data is None
            return FakeResponse(raw={"code": "invalid"})

    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(
        app,
        ["--api-key", "secret", "api", "request", "GET", "sections.json"],
    )

    assert result.exit_code == 1
    assert isinstance(result.exception, ValidationError)


def test_resource_commands_use_client_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    @dataclass(frozen=True, slots=True)
    class FakeResponse:
        raw: JsonObject

    class FakeSections:
        def list(self) -> FakeResponse:
            return FakeResponse(raw={"code": 200, "results": [{"section_id": "s1"}]})

    class FakeAccounts:
        def list_by_type(
            self,
            account: str,
            *,
            section_id: str,
            **params: object,
        ) -> FakeResponse:
            assert account == "assets"
            assert section_id == "s1"
            assert params == {"limit": 5}
            return FakeResponse(raw={"code": 200, "results": [{"account_id": "x1"}]})

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert base_url == "https://whooing.com/api/"
            assert api_key == "secret"
            assert access_token is None
            self.sections = FakeSections()
            self.accounts = FakeAccounts()

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    sections_result = runner.invoke(app, ["--api-key", "secret", "sections", "list"])
    accounts_result = runner.invoke(
        app,
        [
            "--api-key",
            "secret",
            "accounts",
            "list",
            "--section-id",
            "s1",
            "--account",
            "assets",
            "--param",
            "limit=5",
        ],
    )

    assert sections_result.exit_code == 0
    assert accounts_result.exit_code == 0
    assert json.loads(sections_result.stdout)["results"] == [{"section_id": "s1"}]
    assert json.loads(accounts_result.stdout)["results"] == [{"account_id": "x1"}]
