from __future__ import annotations

import json
import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal, TypedDict

import typer

from whooing import WhooingClient, __version__
from whooing.auth import (
    AppAuthClient,
    OAuth1AccessToken,
    OAuth1RequestToken,
    OAuth2Token,
    OAuth2TokenClient,
    build_authorization_url,
    create_pkce_challenge,
)
from whooing.cli_config import (
    default_config_path,
    load_config,
    mask_secret,
    remove_profile,
    save_config,
    set_profile,
)
from whooing.cli_output import render_error, render_output
from whooing.exceptions import WhooingError
from whooing.types import JsonObject, JsonValue, RequestData, RequestValue

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
auth_app = typer.Typer(no_args_is_help=True, help="Authentication helpers")
profile_app = typer.Typer(no_args_is_help=True, help="Manage local CLI profiles")
api_app = typer.Typer(no_args_is_help=True, help="Call Whooing API paths")
user_app = typer.Typer(no_args_is_help=True, help="User API commands")
sections_app = typer.Typer(no_args_is_help=True, help="Section API commands")
accounts_app = typer.Typer(no_args_is_help=True, help="Account API commands")
entries_app = typer.Typer(no_args_is_help=True, help="Entry API commands")
reports_app = typer.Typer(no_args_is_help=True, help="Report API commands")
app.add_typer(auth_app, name="auth")
app.add_typer(profile_app, name="profile")
app.add_typer(api_app, name="api")
app.add_typer(user_app, name="user")
app.add_typer(sections_app, name="sections")
app.add_typer(accounts_app, name="accounts")
app.add_typer(entries_app, name="entries")
app.add_typer(reports_app, name="reports")


@dataclass(frozen=True, slots=True)
class CliState:
    config_path: Path
    profile: str
    output: str
    api_key: str | None
    access_token: str | None
    base_url: str


class _ClientAuthKwargs(TypedDict, total=False):
    api_key: str
    access_token: str


def main(argv: Sequence[str] | None = None) -> int:
    try:
        app(
            args=list(argv) if argv is not None else None,
            prog_name="whooing",
            standalone_mode=False,
        )
    except typer.Exit as exc:
        return int(exc.exit_code)
    except WhooingError as exc:
        typer.echo(render_output(render_error(exc), "json"), err=True)
        return 1
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
    output: Annotated[
        Literal["json", "table", "csv"],
        typer.Option("--output", help="Output format."),
    ] = "json",
    api_key: Annotated[str | None, typer.Option("--api-key", help="Whooing API key.")] = None,
    access_token: Annotated[
        str | None,
        typer.Option("--access-token", help="OAuth bearer access token."),
    ] = None,
    base_url: Annotated[
        str,
        typer.Option("--base-url", help="Whooing API base URL."),
    ] = "https://whooing.com/api/",
) -> None:
    if version:
        typer.echo(f"whooing-py {__version__}")
        raise typer.Exit()
    ctx.obj = CliState(
        config_path=config_path or default_config_path(),
        profile=profile,
        output=output,
        api_key=api_key,
        access_token=access_token,
        base_url=base_url,
    )


@auth_app.command("oauth2-url")
def oauth2_url(
    ctx: typer.Context,
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
    _echo_payload(ctx, payload)


@auth_app.command("exchange-code")
def exchange_code(
    ctx: typer.Context,
    client_id: Annotated[str, typer.Option("--client-id", help="Whooing app client ID.")],
    code: Annotated[str, typer.Option("--code", help="OAuth authorization code.")],
    redirect_uri: Annotated[str, typer.Option("--redirect-uri", help="OAuth callback URI.")],
    code_verifier: Annotated[
        str | None,
        typer.Option("--code-verifier", help="PKCE code verifier."),
    ] = None,
    token_endpoint: Annotated[
        str,
        typer.Option("--token-endpoint", help="OAuth token endpoint."),
    ] = "https://whooing.com/oauth2/token",
) -> None:
    with OAuth2TokenClient(token_endpoint=token_endpoint) as client:
        token = client.exchange_code(
            client_id=client_id,
            code=code,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )
    _echo_payload(ctx, _oauth2_token_payload(token))


@auth_app.command("refresh")
def refresh_token(
    ctx: typer.Context,
    client_id: Annotated[str, typer.Option("--client-id", help="Whooing app client ID.")],
    refresh_token_value: Annotated[
        str,
        typer.Option("--refresh-token", help="OAuth refresh token."),
    ],
    token_endpoint: Annotated[
        str,
        typer.Option("--token-endpoint", help="OAuth token endpoint."),
    ] = "https://whooing.com/oauth2/token",
) -> None:
    with OAuth2TokenClient(token_endpoint=token_endpoint) as client:
        token = client.refresh(client_id=client_id, refresh_token=refresh_token_value)
    _echo_payload(ctx, _oauth2_token_payload(token))


@auth_app.command("revoke")
def revoke_token(
    ctx: typer.Context,
    token: Annotated[str, typer.Option("--token", help="OAuth token to revoke.")],
    revoke_endpoint: Annotated[
        str,
        typer.Option("--revoke-endpoint", help="OAuth revoke endpoint."),
    ] = "https://whooing.com/oauth2/revoke",
) -> None:
    with OAuth2TokenClient(revoke_endpoint=revoke_endpoint) as client:
        payload = client.revoke(token)
    _echo_payload(ctx, payload)


@auth_app.command("oauth1-request-token")
def oauth1_request_token(
    ctx: typer.Context,
    app_id: Annotated[str, typer.Option("--app-id", help="Whooing app ID.")],
    app_secret: Annotated[str, typer.Option("--app-secret", help="Whooing app secret.")],
    callback_uri: Annotated[
        str | None,
        typer.Option("--callback-uri", help="OAuth callback URI."),
    ] = None,
    base_url: Annotated[
        str,
        typer.Option("--base-url", help="Whooing app auth base URL."),
    ] = "https://whooing.com/app_auth/",
) -> None:
    with AppAuthClient(base_url=base_url) as client:
        token = client.request_token(
            app_id=app_id,
            app_secret=app_secret,
            callback_uri=callback_uri,
        )
        authorization_url = client.build_authorization_url(token=token.token)
    _echo_payload(
        ctx,
        {**_oauth1_request_token_payload(token), "authorization_url": authorization_url},
    )


@auth_app.command("oauth1-access-token")
def oauth1_access_token(
    ctx: typer.Context,
    app_id: Annotated[str, typer.Option("--app-id", help="Whooing app ID.")],
    app_secret: Annotated[str, typer.Option("--app-secret", help="Whooing app secret.")],
    token: Annotated[str, typer.Option("--token", help="OAuth request token.")],
    pin: Annotated[str, typer.Option("--pin", help="OAuth verifier PIN.")],
    base_url: Annotated[
        str,
        typer.Option("--base-url", help="Whooing app auth base URL."),
    ] = "https://whooing.com/app_auth/",
) -> None:
    with AppAuthClient(base_url=base_url) as client:
        access_token = client.access_token(
            app_id=app_id,
            app_secret=app_secret,
            token=token,
            pin=pin,
        )
    _echo_payload(ctx, _oauth1_access_token_payload(access_token))


@auth_app.command("onetime")
def onetime_token(
    ctx: typer.Context,
    app_id: Annotated[str, typer.Option("--app-id", help="Whooing app ID.")],
    app_secret: Annotated[str, typer.Option("--app-secret", help="Whooing app secret.")],
    onetime_pin: Annotated[str, typer.Option("--onetime-pin", help="Onetime PIN.")],
    base_url: Annotated[
        str,
        typer.Option("--base-url", help="Whooing app auth base URL."),
    ] = "https://whooing.com/app_auth/",
) -> None:
    with AppAuthClient(base_url=base_url) as client:
        access_token = client.access_token_by_onetime(
            app_id=app_id,
            app_secret=app_secret,
            onetime_pin=onetime_pin,
        )
    _echo_payload(ctx, _oauth1_access_token_payload(access_token))


@api_app.command("request")
def api_request(
    ctx: typer.Context,
    method: Annotated[
        Literal["GET", "POST", "PUT", "DELETE"],
        typer.Argument(help="HTTP method."),
    ],
    path: Annotated[str, typer.Argument(help="API path, for example sections.json.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
    data: Annotated[
        list[str] | None,
        typer.Option("--data", "-d", help="Form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.request(
            method,
            path,
            params=_parse_pairs(param),
            data=_parse_pairs(data),
        )
    _echo_payload(ctx, response.raw)


@user_app.command("get")
def user_get(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.users.get()
    _echo_payload(ctx, response.raw)


@user_app.command("logs")
def user_logs(
    ctx: typer.Context,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.users.logs(**_parse_fields(param))
    _echo_payload(ctx, response.raw)


@sections_app.command("list")
def sections_list(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.list()
    _echo_payload(ctx, response.raw)


@sections_app.command("get")
def sections_get(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Argument(help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.get(section_id)
    _echo_payload(ctx, response.raw)


@sections_app.command("default")
def sections_default(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.default()
    _echo_payload(ctx, response.raw)


@accounts_app.command("list")
def accounts_list(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    account: Annotated[
        str | None,
        typer.Option("--account", help="Optional account group, such as assets or expenses."),
    ] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        if account is None:
            response = client.accounts.list(section_id=section_id, **_parse_fields(param))
        else:
            response = client.accounts.list_by_type(
                account,
                section_id=section_id,
                **_parse_fields(param),
            )
    _echo_payload(ctx, response.raw)


@accounts_app.command("get")
def accounts_get(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    account_id: Annotated[str, typer.Argument(help="Account ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.get(account, account_id, section_id=section_id)
    _echo_payload(ctx, response.raw)


@entries_app.command("list")
def entries_list(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.list(section_id=section_id, **_parse_fields(param))
    _echo_payload(ctx, response.raw)


@entries_app.command("latest")
def entries_latest(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.latest(section_id=section_id, **_parse_fields(param))
    _echo_payload(ctx, response.raw)


@entries_app.command("get")
def entries_get(
    ctx: typer.Context,
    entry_id: Annotated[str, typer.Argument(help="Entry ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.get(entry_id, section_id=section_id)
    _echo_payload(ctx, response.raw)


@reports_app.command("report")
def reports_report(
    ctx: typer.Context,
    account: Annotated[str | None, typer.Option("--account", help="Account group.")] = None,
    account_id: Annotated[str | None, typer.Option("--account-id", help="Account ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.reports.report(account, account_id, **_parse_fields(param))
    _echo_payload(ctx, response.raw)


@reports_app.command("summary")
def reports_summary(
    ctx: typer.Context,
    account: Annotated[str | None, typer.Option("--account", help="Account group.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.reports.summary(account, **_parse_fields(param))
    _echo_payload(ctx, response.raw)


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
    _echo_payload(ctx, {"profile": state.profile, "saved": True})


@profile_app.command("show")
def profile_show(ctx: typer.Context) -> None:
    state = _state(ctx)
    profile = load_config(state.config_path).profiles.get(state.profile)
    if profile is None:
        raise typer.BadParameter(f"Profile not found: {state.profile}")
    _echo_payload(
        ctx,
        {
            "profile": state.profile,
            "api_key": mask_secret(profile.api_key),
            "access_token": mask_secret(profile.access_token),
        },
    )


@profile_app.command("list")
def profile_list(ctx: typer.Context) -> None:
    config = load_config(_state(ctx).config_path)
    profiles: list[JsonValue] = [name for name in sorted(config.profiles)]
    _echo_payload(ctx, {"profiles": profiles})


@profile_app.command("remove")
def profile_remove(ctx: typer.Context) -> None:
    state = _state(ctx)
    config = remove_profile(load_config(state.config_path), name=state.profile)
    save_config(state.config_path, config)
    _echo_payload(ctx, {"profile": state.profile, "removed": True})


def _state(ctx: typer.Context) -> CliState:
    if not isinstance(ctx.obj, CliState):
        msg = "CLI context is not initialized."
        raise RuntimeError(msg)
    return ctx.obj


def _echo_payload(ctx: typer.Context, payload: JsonValue) -> None:
    typer.echo(render_output(payload, _state(ctx).output))


@contextmanager
def _client_from_state(state: CliState) -> Iterator[WhooingClient]:
    auth_kwargs = _auth_kwargs(state)
    with WhooingClient(base_url=state.base_url, **auth_kwargs) as client:
        yield client


def _auth_kwargs(state: CliState) -> _ClientAuthKwargs:
    if state.api_key is not None and state.access_token is not None:
        raise typer.BadParameter("Provide only one of --api-key or --access-token.")
    if state.api_key is not None:
        return {"api_key": state.api_key}
    if state.access_token is not None:
        return {"access_token": state.access_token}

    env_api_key = os.environ.get("WHOOING_API_KEY")
    env_access_token = os.environ.get("WHOOING_ACCESS_TOKEN")
    if env_api_key is not None and env_access_token is not None:
        raise typer.BadParameter("Set only one of WHOOING_API_KEY or WHOOING_ACCESS_TOKEN.")
    if env_api_key is not None:
        return {"api_key": env_api_key}
    if env_access_token is not None:
        return {"access_token": env_access_token}

    profile = load_config(state.config_path).profiles.get(state.profile)
    if profile is not None:
        if profile.access_token is not None:
            return {"access_token": profile.access_token}
        if profile.api_key is not None:
            return {"api_key": profile.api_key}

    raise typer.BadParameter(
        "Authentication is required. Provide --api-key, --access-token, environment variables, "
        "or a saved profile."
    )


def _parse_pairs(values: list[str] | None) -> RequestData | None:
    if values is None:
        return None
    data: dict[str, RequestValue] = {}
    for value in values:
        key, separator, raw = value.partition("=")
        if not separator or not key:
            raise typer.BadParameter(f"Expected key=value: {value}")
        data[key] = _parse_request_value(raw)
    return data


def _parse_fields(values: list[str] | None) -> dict[str, RequestValue]:
    return dict(_parse_pairs(values) or {})


def _parse_request_value(value: str) -> RequestValue:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return value
    if parsed is None or isinstance(parsed, str | int | float | bool):
        return parsed
    if isinstance(parsed, list) and all(
        item is None or isinstance(item, str | int | float | bool) for item in parsed
    ):
        return parsed
    return value


def _oauth2_token_payload(token: OAuth2Token) -> JsonObject:
    return {
        "access_token": token.access_token,
        "token_type": token.token_type,
        "expires_in": token.expires_in,
        "refresh_token": token.refresh_token,
        "scope": token.scope,
        "raw": token.raw,
    }


def _oauth1_request_token_payload(token: OAuth1RequestToken) -> JsonObject:
    return {"token": token.token, "raw": token.raw}


def _oauth1_access_token_payload(token: OAuth1AccessToken) -> JsonObject:
    return {
        "token": token.token,
        "token_secret": token.token_secret,
        "user_id": token.user_id,
        "raw": token.raw,
    }
