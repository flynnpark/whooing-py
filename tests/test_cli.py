from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from urllib.parse import parse_qs, urlparse

from typer.testing import CliRunner

from whooing.cli import app
from whooing.types import JsonObject

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
