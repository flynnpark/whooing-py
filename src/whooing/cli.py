from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Annotated

import typer

from whooing import __version__
from whooing.auth import build_authorization_url, create_pkce_challenge
from whooing.types import JsonObject

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
auth_app = typer.Typer(no_args_is_help=True, help="Authentication helpers")
app.add_typer(auth_app, name="auth")


def main(argv: Sequence[str] | None = None) -> int:
    app(args=list(argv) if argv is not None else None, prog_name="whooing")
    return 0


@app.callback()
def _root(
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the installed whooing-py version."),
    ] = False,
) -> None:
    if version:
        typer.echo(f"whooing-py {__version__}")
        raise typer.Exit()


@auth_app.command("oauth2-url")
def oauth2_url(
    client_id: Annotated[str, typer.Option("--client-id", help="Whooing app client ID.")],
    redirect_uri: Annotated[str, typer.Option("--redirect-uri", help="OAuth callback URI.")],
    scope: Annotated[
        list[str] | None,
        typer.Option("--scope", help="OAuth scope. Repeat for multiple scopes."),
    ] = None,
    state: Annotated[str | None, typer.Option("--state", help="Optional CSRF state.")] = None,
) -> None:
    challenge = create_pkce_challenge()
    payload: JsonObject = {
        "authorization_url": build_authorization_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scopes=scope or [],
            state=state,
            challenge=challenge,
        ),
        "code_verifier": challenge.verifier,
        "code_challenge": challenge.challenge,
        "code_challenge_method": challenge.method,
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
