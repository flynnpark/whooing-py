from __future__ import annotations

import json
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
