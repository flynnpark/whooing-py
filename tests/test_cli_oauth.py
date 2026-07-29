from __future__ import annotations

import http.client
import threading
from typing import cast
from urllib.parse import parse_qs, urlencode, urlparse

import pytest

from whooing.cli_oauth import OAuthCallbackError, authorize_in_browser


def test_authorize_in_browser_receives_loopback_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    callback_thread: threading.Thread | None = None

    def open_browser(authorization_url: str) -> bool:
        nonlocal callback_thread
        query = parse_qs(urlparse(authorization_url).query)
        redirect_uri = query["redirect_uri"][0]
        state = query["state"][0]

        def send_callback() -> None:
            redirect = urlparse(redirect_uri)
            connection = http.client.HTTPConnection("127.0.0.1", redirect.port, timeout=2)
            connection.request(
                "GET",
                f"{redirect.path}?{urlencode({'code': 'code', 'state': state})}",
            )
            response = connection.getresponse()
            assert response.status == 200
            response.read()
            connection.close()

        callback_thread = threading.Thread(target=send_callback)
        callback_thread.start()
        return True

    monkeypatch.setattr("whooing.cli_oauth.webbrowser.open", open_browser)

    authorization = authorize_in_browser(
        client_id="app",
        scopes=["read"],
        timeout_seconds=2,
        open_browser=True,
        authorization_endpoint="https://authorize.example",
    )
    cast(threading.Thread, callback_thread).join(timeout=2)

    assert authorization.code == "code"
    assert authorization.code_verifier
    assert authorization.redirect_uri.startswith("http://localhost:")


def test_authorize_in_browser_rejects_mismatched_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    callback_thread: threading.Thread | None = None

    def open_browser(authorization_url: str) -> bool:
        nonlocal callback_thread
        query = parse_qs(urlparse(authorization_url).query)
        redirect_uri = query["redirect_uri"][0]

        def send_callback() -> None:
            redirect = urlparse(redirect_uri)
            connection = http.client.HTTPConnection("127.0.0.1", redirect.port, timeout=2)
            connection.request(
                "GET",
                f"{redirect.path}?{urlencode({'code': 'code', 'state': 'wrong'})}",
            )
            response = connection.getresponse()
            response.read()
            connection.close()

        callback_thread = threading.Thread(target=send_callback)
        callback_thread.start()
        return True

    monkeypatch.setattr("whooing.cli_oauth.webbrowser.open", open_browser)

    with pytest.raises(OAuthCallbackError, match="state did not match"):
        authorize_in_browser(
            client_id="app",
            scopes=["read"],
            timeout_seconds=2,
            open_browser=True,
        )
    cast(threading.Thread, callback_thread).join(timeout=2)
