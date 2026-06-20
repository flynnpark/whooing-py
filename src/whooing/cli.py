from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from typing import cast

from whooing import __version__
from whooing.auth import build_authorization_url, create_pkce_challenge
from whooing.types import JsonObject, JsonValue


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    handler = cast(Callable[[argparse.Namespace], int] | None, getattr(args, "handler", None))
    if handler is None:
        parser.print_help()
        return 2
    return handler(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="whooing")
    parser.add_argument("--version", action="version", version=f"whooing-py {__version__}")

    subcommands = parser.add_subparsers(dest="command")
    auth = subcommands.add_parser("auth", help="Authentication helpers")
    auth_subcommands = auth.add_subparsers(dest="auth_command")

    oauth2_url = auth_subcommands.add_parser(
        "oauth2-url",
        help="Build an OAuth 2.0 PKCE authorization URL",
    )
    oauth2_url.add_argument("--client-id", required=True)
    oauth2_url.add_argument("--redirect-uri", required=True)
    oauth2_url.add_argument("--scope", action="append", default=[])
    oauth2_url.add_argument("--state")
    oauth2_url.set_defaults(handler=_handle_oauth2_url)

    return parser


def _handle_oauth2_url(args: argparse.Namespace) -> int:
    challenge = create_pkce_challenge()
    payload: JsonObject = {
        "authorization_url": build_authorization_url(
            client_id=args.client_id,
            redirect_uri=args.redirect_uri,
            scopes=args.scope,
            state=args.state,
            challenge=challenge,
        ),
        "code_verifier": challenge.verifier,
        "code_challenge": challenge.challenge,
        "code_challenge_method": challenge.method,
    }
    _write_json(payload)
    return 0


def _write_json(value: JsonValue) -> None:
    sys.stdout.write(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    sys.stdout.write("\n")
