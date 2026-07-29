from __future__ import annotations

import html
import secrets
import sys
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import TCPServer
from typing import cast
from urllib.parse import parse_qs, urlsplit

from whooing.auth import build_authorization_url, create_pkce_challenge


class OAuthCallbackError(ValueError):
    """Raised when the local OAuth callback cannot complete safely."""


@dataclass(frozen=True, slots=True)
class OAuthAuthorizationCode:
    code: str
    code_verifier: str
    redirect_uri: str


@dataclass(frozen=True, slots=True)
class _CallbackResult:
    code: str | None
    state: str | None
    error: str | None
    error_description: str | None


class _OAuthCallbackServer(HTTPServer):
    callback_path: str
    result: _CallbackResult | None

    def __init__(self, callback_path: str) -> None:
        super().__init__(("127.0.0.1", 0), _OAuthCallbackHandler)
        self.callback_path = callback_path
        self.result = None

    def server_bind(self) -> None:
        # HTTPServer performs a reverse DNS lookup that is unnecessary for a loopback callback.
        TCPServer.server_bind(self)
        host, port = cast(tuple[str, int], self.server_address)
        self.server_name = host
        self.server_port = port


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    server: _OAuthCallbackServer

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path != self.server.callback_path:
            self.send_error(404)
            return

        query = parse_qs(parsed.query)
        self.server.result = _CallbackResult(
            code=_first_value(query, "code"),
            state=_first_value(query, "state"),
            error=_first_value(query, "error"),
            error_description=_first_value(query, "error_description"),
        )
        if self.server.result.error is None:
            self._send_html(
                200,
                "후잉 인증이 완료되었습니다. 이 창을 닫고 터미널로 돌아가세요.",
            )
        else:
            self._send_html(
                400,
                "후잉 인증이 완료되지 않았습니다. 터미널에서 오류를 확인하세요.",
            )

    def log_message(self, format_string: str, *args: object) -> None:
        return None

    def _send_html(self, status: int, message: str) -> None:
        body = (
            '<!doctype html><html lang="ko"><meta charset="utf-8">'
            f"<title>whooing-py</title><body><p>{html.escape(message)}</p></body></html>"
        ).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def authorize_in_browser(
    *,
    client_id: str,
    scopes: list[str],
    timeout_seconds: float,
    open_browser: bool,
    authorization_endpoint: str = "https://whooing.com/oauth2/authorize",
) -> OAuthAuthorizationCode:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero.")

    callback_path = "/callback"
    state = secrets.token_urlsafe(32)
    challenge = create_pkce_challenge()
    with _OAuthCallbackServer(callback_path) as server:
        port = cast(tuple[str, int], server.server_address)[1]
        redirect_uri = f"http://localhost:{port}{callback_path}"
        authorization_url = build_authorization_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scopes=scopes,
            state=state,
            challenge=challenge,
            authorization_endpoint=authorization_endpoint,
        )
        print(
            f"Open this URL to authorize whooing-py:\n{authorization_url}",
            file=sys.stderr,
            flush=True,
        )
        if open_browser and not webbrowser.open(authorization_url):
            print(
                "Unable to open a browser automatically. Open the URL above.",
                file=sys.stderr,
                flush=True,
            )

        result = _wait_for_callback(server, timeout_seconds)

    if result.state != state:
        raise OAuthCallbackError("OAuth callback state did not match the login request.")
    if result.error is not None:
        detail = f": {result.error_description}" if result.error_description else ""
        raise OAuthCallbackError(f"Whooing authorization failed ({result.error}){detail}")
    if result.code is None:
        raise OAuthCallbackError("OAuth callback did not include an authorization code.")
    return OAuthAuthorizationCode(
        code=result.code,
        code_verifier=challenge.verifier,
        redirect_uri=redirect_uri,
    )


def _wait_for_callback(
    server: _OAuthCallbackServer,
    timeout_seconds: float,
) -> _CallbackResult:
    deadline = time.monotonic() + timeout_seconds
    while server.result is None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise OAuthCallbackError("Timed out waiting for Whooing authorization.")
        server.timeout = min(remaining, 1.0)
        server.handle_request()
    return server.result


def _first_value(query: dict[str, list[str]], name: str) -> str | None:
    values = query.get(name)
    if not values or not values[0]:
        return None
    return values[0]
