from __future__ import annotations

import json
from typing import cast
from urllib.parse import parse_qs, urlparse

from _pytest.capture import CaptureFixture

from whooing.cli import main
from whooing.types import JsonObject


def test_oauth2_url_command_outputs_pkce_payload(capsys: CaptureFixture[str]) -> None:
    exit_code = main(
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

    captured = capsys.readouterr()
    payload = cast(JsonObject, json.loads(captured.out))
    authorization_url = urlparse(str(payload["authorization_url"]))
    query = parse_qs(authorization_url.query)

    assert exit_code == 0
    assert query["client_id"] == ["app"]
    assert query["redirect_uri"] == ["http://localhost/callback"]
    assert query["scope"] == ["read,write"]
    assert query["state"] == ["state"]
    assert query["code_challenge"] == [payload["code_challenge"]]
    assert payload["code_challenge_method"] == "S256"
