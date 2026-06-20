from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from whooing import __version__
from whooing.auth import build_authorization_url, create_pkce_challenge
from whooing.cli_config import (
    default_config_path,
    load_config,
    mask_secret,
    remove_profile,
    save_config,
    set_profile,
)
from whooing.types import JsonObject, JsonValue

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
auth_app = typer.Typer(no_args_is_help=True, help="Authentication helpers")
profile_app = typer.Typer(no_args_is_help=True, help="Manage local CLI profiles")
app.add_typer(auth_app, name="auth")
app.add_typer(profile_app, name="profile")


@dataclass(frozen=True, slots=True)
class CliState:
    config_path: Path
    profile: str


def main(argv: Sequence[str] | None = None) -> int:
    app(args=list(argv) if argv is not None else None, prog_name="whooing")
    return 0


@app.callback()
def _root(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the installed whooing-py version."),
    ] = False,
    config_path: Annotated[
        Path | None,
        typer.Option("--config", help="Path to the CLI config JSON file."),
    ] = None,
    profile: Annotated[
        str,
        typer.Option("--profile", help="CLI profile name."),
    ] = "default",
) -> None:
    if version:
        typer.echo(f"whooing-py {__version__}")
        raise typer.Exit()
    ctx.obj = CliState(config_path=config_path or default_config_path(), profile=profile)


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


@profile_app.command("set")
def profile_set(
    ctx: typer.Context,
    api_key: Annotated[str | None, typer.Option("--api-key", help="Whooing API key.")] = None,
    access_token: Annotated[
        str | None,
        typer.Option("--access-token", help="OAuth bearer access token."),
    ] = None,
) -> None:
    if api_key is None and access_token is None:
        raise typer.BadParameter("Provide at least one of --api-key or --access-token.")
    state = _state(ctx)
    config = set_profile(
        load_config(state.config_path),
        name=state.profile,
        api_key=api_key,
        access_token=access_token,
    )
    save_config(state.config_path, config)
    _echo_json({"profile": state.profile, "saved": True})


@profile_app.command("show")
def profile_show(ctx: typer.Context) -> None:
    state = _state(ctx)
    profile = load_config(state.config_path).profiles.get(state.profile)
    if profile is None:
        raise typer.BadParameter(f"Profile not found: {state.profile}")
    _echo_json(
        {
            "profile": state.profile,
            "api_key": mask_secret(profile.api_key),
            "access_token": mask_secret(profile.access_token),
        }
    )


@profile_app.command("list")
def profile_list(ctx: typer.Context) -> None:
    config = load_config(_state(ctx).config_path)
    profiles: list[JsonValue] = [name for name in sorted(config.profiles)]
    _echo_json({"profiles": profiles})


@profile_app.command("remove")
def profile_remove(ctx: typer.Context) -> None:
    state = _state(ctx)
    config = remove_profile(load_config(state.config_path), name=state.profile)
    save_config(state.config_path, config)
    _echo_json({"profile": state.profile, "removed": True})


def _state(ctx: typer.Context) -> CliState:
    if not isinstance(ctx.obj, CliState):
        msg = "CLI context is not initialized."
        raise RuntimeError(msg)
    return ctx.obj


def _echo_json(payload: JsonObject) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
