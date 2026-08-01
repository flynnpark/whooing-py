from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

import pytest
from pydantic import ValidationError
from typer.core import TyperGroup
from typer.main import get_command
from typer.testing import CliRunner

from whooing import __version__
from whooing.auth import OAuth1RequestToken, OAuth2Token
from whooing.cli import app, main
from whooing.cli_config import CliConfig, CliProfile, load_config, save_config
from whooing.cli_oauth import OAuthAuthorizationCode
from whooing.response import ApiResponse
from whooing.types import JsonObject, JsonValue, RequestData

runner = CliRunner()
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
SAFETY_HELP_PREFIXES = (
    "[READ]",
    "[WRITE]",
    "[LOCAL READ]",
    "[LOCAL WRITE]",
    "[AUTH]",
    "[DYNAMIC]",
)


def strip_ansi(value: str) -> str:
    return ANSI_PATTERN.sub("", value)


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
        ],
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


def test_oauth_login_completes_oauth_and_saves_default_section(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"

    def authorize_in_browser(
        *,
        client_id: str,
        scopes: list[str],
        timeout_seconds: float,
        open_browser: bool,
        authorization_endpoint: str,
    ) -> OAuthAuthorizationCode:
        assert client_id == "app"
        assert scopes == ["read"]
        assert timeout_seconds == 180.0
        assert open_browser is True
        assert authorization_endpoint == "https://whooing.com/oauth2/authorize"
        return OAuthAuthorizationCode(
            code="code",
            code_verifier="verifier",
            redirect_uri="http://localhost:1234/callback",
        )

    class FakeOAuth2TokenClient:
        def __init__(self, *, token_endpoint: str = "", revoke_endpoint: str = "") -> None:
            assert token_endpoint == "https://whooing.com/oauth2/token"

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
            assert client_id == "app"
            assert code == "code"
            assert redirect_uri == "http://localhost:1234/callback"
            assert code_verifier == "verifier"
            return OAuth2Token(
                access_token="access",
                token_type="Bearer",
                expires_in=3600,
                refresh_token="refresh",
                scope="read",
                raw={"access_token": "access"},
            )

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert base_url == "https://whooing.com/api/"
            assert api_key is None
            assert access_token == "access"
            self.sections = self

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def default(self) -> ApiResponse[JsonValue]:
            raw: JsonObject = {
                "code": 200,
                "results": {"section_id": "s123", "title": "생활비"},
            }
            return ApiResponse(
                code=200,
                message="",
                rest_of_api=100,
                error_parameters={},
                results=raw["results"],
                raw=raw,
            )

    monkeypatch.setattr("whooing.cli.authorize_in_browser", authorize_in_browser)
    monkeypatch.setattr("whooing.cli.OAuth2TokenClient", FakeOAuth2TokenClient)
    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(
        app,
        ["--config", str(config_path), "auth", "oauth-login", "--client-id", "app"],
    )

    profile = load_config(config_path).profiles["default"]
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "authenticated": True,
        "profile": "default",
        "scope": "read",
        "section_id": "s123",
    }
    assert profile.access_token == "access"
    assert profile.refresh_token == "refresh"
    assert profile.oauth_client_id == "app"
    assert profile.section_id == "s123"


def test_login_prompts_for_ai_integration_key_and_saves_default_section(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"

    def open_browser(url: str) -> bool:
        assert url == "https://whooing.com"
        return True

    def prompt(text: str, *, hide_input: bool, err: bool) -> str:
        assert text == "Whooing AI integration API key"
        assert hide_input is True
        assert err is True
        return "api-key"

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert base_url == "https://whooing.com/api/"
            assert api_key == "api-key"
            assert access_token is None
            self.sections = self

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def default(self) -> ApiResponse[JsonValue]:
            raw: JsonObject = {
                "code": 200,
                "results": {"section_id": "s123", "title": "생활비"},
            }
            return ApiResponse(
                code=200,
                message="",
                rest_of_api=100,
                error_parameters={},
                results=raw["results"],
                raw=raw,
            )

    monkeypatch.setattr("whooing.cli.webbrowser.open", open_browser)
    monkeypatch.setattr("whooing.cli.typer.prompt", prompt)
    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(
        app,
        ["--config", str(config_path), "auth", "login"],
    )

    profile = load_config(config_path).profiles["default"]
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "authenticated": True,
        "auth_method": "api_key",
        "profile": "default",
        "section_id": "s123",
    }
    assert profile.api_key == "api-key"
    assert profile.section_id == "s123"
    assert "api-key" not in result.output


def test_auth_status_does_not_expose_saved_tokens(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    save_config(
        config_path,
        CliConfig(
            profiles={
                "default": CliProfile(
                    access_token="access-secret",
                    refresh_token="refresh-secret",
                    oauth_client_id="app",
                    oauth_scope="read",
                    section_id="s123",
                )
            }
        ),
    )

    result = runner.invoke(app, ["--config", str(config_path), "auth", "status"])

    assert result.exit_code == 0
    assert "access-secret" not in result.stdout
    assert "refresh-secret" not in result.stdout
    assert json.loads(result.stdout) == {
        "auth_method": "oauth2",
        "authenticated": True,
        "client_id": "app",
        "profile": "default",
        "scope": "read",
        "section_id": "s123",
    }


def test_logout_revokes_refresh_token_and_removes_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    save_config(
        config_path,
        CliConfig(
            profiles={
                "default": CliProfile(
                    access_token="access",
                    refresh_token="refresh",
                    oauth_client_id="app",
                )
            }
        ),
    )

    class FakeOAuth2TokenClient:
        def __init__(self, *, token_endpoint: str = "", revoke_endpoint: str = "") -> None:
            assert revoke_endpoint == "https://whooing.com/oauth2/revoke"

        def __enter__(self) -> FakeOAuth2TokenClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def revoke(self, token: str) -> JsonObject:
            assert token == "refresh"
            return {}

    monkeypatch.setattr("whooing.cli.OAuth2TokenClient", FakeOAuth2TokenClient)

    result = runner.invoke(app, ["--config", str(config_path), "auth", "logout"])

    assert result.exit_code == 0
    assert load_config(config_path).profiles == {}
    assert json.loads(result.stdout)["revoked"] is True


def test_version_option_outputs_package_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"whooing-py {__version__}\n"


def test_main_without_args_shows_help_without_traceback(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])
    captured = capsys.readouterr()
    output = strip_ansi(captured.out)

    assert exit_code == 0
    assert "Usage: whooing" in output
    assert "Traceback" not in output
    assert captured.err == ""


def test_main_click_error_shows_message_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    exit_code = main(["--config", str(tmp_path / "config.json"), "profile", "show"])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert captured.out == ""
    assert "Profile not found: default" in captured.err
    assert "Invalid value" not in captured.err
    assert "Traceback" not in captured.err


def test_main_auth_error_shows_message_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("WHOOING_API_KEY", raising=False)
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    exit_code = main(["--config", str(tmp_path / "config.json"), "sections", "list"])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert captured.out == ""
    assert "Authentication is required" in captured.err
    assert "Invalid value" not in captured.err
    assert "Traceback" not in captured.err


def test_profile_set_requires_explicit_from_env_for_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "config.json"
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("WHOOING_API_KEY=dotenv-secret\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("WHOOING_API_KEY", raising=False)
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    set_result = main(["--config", str(config_path), "profile", "set"])
    captured = capsys.readouterr()

    assert set_result != 0
    assert "Provide --api-key, --access-token, or --from-env." in captured.err


def test_profile_set_from_env_loads_credentials_from_dotenv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("WHOOING_API_KEY=dotenv-secret\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("WHOOING_API_KEY", raising=False)
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    set_result = main(["--config", str(config_path), "profile", "set", "--from-env"])
    show_result = runner.invoke(app, ["--config", str(config_path), "profile", "show"])

    assert set_result == 0
    assert show_result.exit_code == 0
    assert json.loads(show_result.stdout)["api_key"] == "dote...cret"


def test_empty_environment_credentials_do_not_override_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "profile",
            "set",
            "--api-key",
            "profile-secret",
        ],
    )
    monkeypatch.setenv("WHOOING_API_KEY", "")
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert base_url == "https://whooing.com/api/"
            assert api_key == "profile-secret"
            assert access_token is None
            self.sections = self

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

        def list(self) -> ApiResponse[JsonValue]:
            return ApiResponse(
                code=200,
                message="",
                rest_of_api=1,
                error_parameters={},
                results=[],
                raw={"code": 200, "results": []},
            )

    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(app, ["--config", str(config_path), "sections", "list"])

    assert result.exit_code == 0


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


def test_every_leaf_command_help_declares_safety_and_behavior() -> None:
    root_command = get_command(app)

    assert isinstance(root_command, TyperGroup)
    for group_name, group_command in root_command.commands.items():
        assert group_command.help, f"Missing help for command group: {group_name}"
        assert isinstance(group_command, TyperGroup)
        for command_name, command in group_command.commands.items():
            assert command.help, f"Missing help for command: {group_name} {command_name}"
            assert command.help.startswith(SAFETY_HELP_PREFIXES), (
                f"Missing safety prefix for command: {group_name} {command_name}"
            )


def test_resource_help_explains_read_and_write_commands() -> None:
    result = runner.invoke(app, ["entries", "--help"])

    assert result.exit_code == 0
    assert "[READ] List transactions using optional API filters." in result.stdout
    assert "[WRITE] Create a transaction from form fields." in result.stdout


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


def test_profile_set_rejects_multiple_authentication_methods(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"

    exit_code = main(
        [
            "--config",
            str(config_path),
            "profile",
            "set",
            "--api-key",
            "key",
            "--access-token",
            "token",
        ]
    )

    assert exit_code != 0
    assert not config_path.exists()


def test_main_reports_invalid_profile_config_without_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{", encoding="utf-8")

    exit_code = main(["--config", str(config_path), "profile", "list"])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert "Unable to read CLI config" in captured.err
    assert "Traceback" not in captured.err


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


def test_resource_command_uses_section_saved_in_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "profile",
            "set",
            "--api-key",
            "secret",
            "--section-id",
            "s123",
        ],
    )
    monkeypatch.delenv("WHOOING_SECTION_ID", raising=False)
    monkeypatch.delenv("WHOOING_API_KEY", raising=False)
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    class FakeAccounts:
        def list(self, *, section_id: str, **params: object) -> ApiResponse[JsonValue]:
            assert section_id == "s123"
            assert params == {}
            raw: JsonObject = {"code": 200, "results": {}}
            return ApiResponse(
                code=200,
                message="",
                rest_of_api=100,
                error_parameters={},
                results={},
                raw=raw,
            )

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            assert api_key == "secret"
            self.accounts = FakeAccounts()

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(
        app,
        ["--config", str(config_path), "accounts", "list"],
    )

    assert result.exit_code == 0


def test_explicit_section_overrides_environment_and_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "profile",
            "set",
            "--api-key",
            "secret",
            "--section-id",
            "profile-section",
        ],
    )
    monkeypatch.setenv("WHOOING_SECTION_ID", "environment-section")
    monkeypatch.delenv("WHOOING_API_KEY", raising=False)
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    class FakeAccounts:
        def list(self, *, section_id: str, **params: object) -> ApiResponse[JsonValue]:
            assert section_id == "explicit-section"
            raw: JsonObject = {"code": 200, "results": {}}
            return ApiResponse(
                code=200,
                message="",
                rest_of_api=100,
                error_parameters={},
                results={},
                raw=raw,
            )

    class FakeWhooingClient:
        def __init__(
            self,
            *,
            base_url: str,
            api_key: str | None = None,
            access_token: str | None = None,
        ) -> None:
            self.accounts = FakeAccounts()

        def __enter__(self) -> FakeWhooingClient:
            return self

        def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
            return None

    monkeypatch.setattr("whooing.cli.WhooingClient", FakeWhooingClient)

    result = runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "accounts",
            "list",
            "--section-id",
            "explicit-section",
        ],
    )

    assert result.exit_code == 0


def test_resource_command_explains_how_to_configure_missing_section(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    runner.invoke(
        app,
        [
            "--config",
            str(config_path),
            "profile",
            "set",
            "--api-key",
            "secret",
        ],
    )
    monkeypatch.delenv("WHOOING_SECTION_ID", raising=False)
    monkeypatch.delenv("WHOOING_API_KEY", raising=False)
    monkeypatch.delenv("WHOOING_ACCESS_TOKEN", raising=False)

    result = runner.invoke(
        app,
        ["--config", str(config_path), "accounts", "list"],
    )

    assert result.exit_code != 0
    assert "profile set --section-id" in strip_ansi(result.output)
