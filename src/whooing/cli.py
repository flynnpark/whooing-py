from __future__ import annotations

import json
import os
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal, Protocol, TypedDict, TypeVar, cast

import typer
from dotenv import load_dotenv
from pydantic import TypeAdapter, ValidationError
from typer._click.exceptions import ClickException, NoArgsIsHelpError

from whooing import WhooingClient, __version__
from whooing._pydantic_models.base import WhooingEnvelope
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
from whooing.pydantic_models import (
    AccountExistenceResponse,
    AccountResponse,
    AccountsByTypeResponse,
    AccountsResponse,
    BbsCommentsResponse,
    BbsPostResponse,
    BbsPostsResponse,
    BillsListResponse,
    BillsResponse,
    BudgetGoalResponse,
    BudgetReportResponse,
    BudgetsResponse,
    CalendarResponse,
    CapitalGoalResponse,
    CheckcardsListResponse,
    CheckcardsResponse,
    CustomReportRowsResponse,
    EntriesListResponse,
    EntriesResponse,
    EntryAnalysisResponse,
    EntryChangeResponse,
    EntryFlowResponse,
    EntryNameAmountResponse,
    EntryResponse,
    FrequentItemsResponse,
    FrequentItemsSlotsResponse,
    InOutAccountResponse,
    InOutListResponse,
    InOutResponse,
    MessagesResponse,
    MonthlyItemsListResponse,
    MonthlyItemsResponse,
    NotificationsResponse,
    OAuth1AccessTokenResponse,
    OAuth1RequestTokenResponse,
    OAuth2TokenResponse,
    PostItResponse,
    PostItsResponse,
    ReportResponse,
    ReportsListResponse,
    ReportSummaryResponse,
    SectionResponse,
    SectionsResponse,
    UnreadMessagesResponse,
    UploadInfoResponse,
    UserLogsResponse,
    UserPointLogsResponse,
    UserResponse,
)
from whooing.response import ApiResponse
from whooing.types import JsonObject, JsonValue, RequestData, RequestValue

app = typer.Typer(no_args_is_help=True, invoke_without_command=True)
auth_app = typer.Typer(no_args_is_help=True, help="Authentication helpers")
profile_app = typer.Typer(no_args_is_help=True, help="Manage local CLI profiles")
api_app = typer.Typer(no_args_is_help=True, help="Call Whooing API paths")
user_app = typer.Typer(no_args_is_help=True, help="User API commands")
sections_app = typer.Typer(no_args_is_help=True, help="Section API commands")
accounts_app = typer.Typer(no_args_is_help=True, help="Account API commands")
entries_app = typer.Typer(no_args_is_help=True, help="Entry API commands")
budgets_app = typer.Typer(no_args_is_help=True, help="Budget API commands")
reports_app = typer.Typer(no_args_is_help=True, help="Report API commands")
extras_app = typer.Typer(no_args_is_help=True, help="Extra API commands")
app.add_typer(auth_app, name="auth")
app.add_typer(profile_app, name="profile")
app.add_typer(api_app, name="api")
app.add_typer(user_app, name="user")
app.add_typer(sections_app, name="sections")
app.add_typer(accounts_app, name="accounts")
app.add_typer(entries_app, name="entries")
app.add_typer(budgets_app, name="budgets")
app.add_typer(reports_app, name="reports")
app.add_typer(extras_app, name="extras")

ResponseModelT = TypeVar("ResponseModelT", covariant=True)
RequestDataAdapter: TypeAdapter[dict[str, RequestValue]] = TypeAdapter(dict[str, RequestValue])


class PydanticModel(Protocol[ResponseModelT]):
    @classmethod
    def model_validate(cls, obj: object) -> ResponseModelT: ...


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
    load_dotenv(Path.cwd() / ".env")
    try:
        app(
            args=list(argv) if argv is not None else None,
            prog_name="whooing",
            standalone_mode=False,
        )
    except typer.Exit as exc:
        return int(exc.exit_code)
    except NoArgsIsHelpError:
        return 0
    except ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    except WhooingError as exc:
        typer.echo(render_output(render_error(exc), "json"), err=True)
        return 1
    except ValidationError as exc:
        payload: JsonObject = {
            "error": "validation_error",
            "details": cast(JsonValue, exc.errors()),
        }
        typer.echo(render_output(payload, "json"), err=True)
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
    _echo_payload_model(ctx, _oauth2_token_payload(token), OAuth2TokenResponse)


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
    _echo_payload_model(ctx, _oauth2_token_payload(token), OAuth2TokenResponse)


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
    _echo_payload_model(
        ctx,
        {**_oauth1_request_token_payload(token), "authorization_url": authorization_url},
        OAuth1RequestTokenResponse,
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
    _echo_payload_model(ctx, _oauth1_access_token_payload(access_token), OAuth1AccessTokenResponse)


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
    _echo_payload_model(ctx, _oauth1_access_token_payload(access_token), OAuth1AccessTokenResponse)


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
    _echo_response(ctx, response, WhooingEnvelope)


@user_app.command("get")
def user_get(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.users.get()
    _echo_response(ctx, response, UserResponse)


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
    _echo_response(ctx, response, UserLogsResponse)


@user_app.command("point-logs")
def user_point_logs(
    ctx: typer.Context,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.users.point_logs(**_parse_fields(param))
    _echo_response(ctx, response, UserPointLogsResponse)


@user_app.command("update")
def user_update(
    ctx: typer.Context,
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.users.update(**_parse_fields(field))
    _echo_response(ctx, response, UserResponse)


@sections_app.command("list")
def sections_list(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.list()
    _echo_response(ctx, response, SectionsResponse)


@sections_app.command("get")
def sections_get(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Argument(help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.get(section_id)
    _echo_response(ctx, response, SectionResponse)


@sections_app.command("default")
def sections_default(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.default()
    _echo_response(ctx, response, SectionResponse)


@sections_app.command("create")
def sections_create(
    ctx: typer.Context,
    title: Annotated[str, typer.Option("--title", help="Section title.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.create(title=title, **_parse_fields(field))
    _echo_response(ctx, response, SectionResponse)


@sections_app.command("update")
def sections_update(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Argument(help="Section ID.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.update(section_id, **_parse_fields(field))
    _echo_response(ctx, response, SectionResponse)


@sections_app.command("delete")
def sections_delete(
    ctx: typer.Context,
    section_id: Annotated[list[str], typer.Argument(help="Section ID. Repeatable.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.delete(section_id)
    _echo_response(ctx, response, WhooingEnvelope)


@sections_app.command("sort")
def sections_sort(
    ctx: typer.Context,
    section_id: Annotated[list[str], typer.Argument(help="Section IDs in desired order.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.sections.sort(section_id)
    _echo_response(ctx, response, WhooingEnvelope)


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
            _echo_response(ctx, response, AccountsResponse)
        else:
            response = client.accounts.list_by_type(
                account,
                section_id=section_id,
                **_parse_fields(param),
            )
            _echo_response(ctx, response, AccountsByTypeResponse)


@accounts_app.command("get")
def accounts_get(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    account_id: Annotated[str, typer.Argument(help="Account ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.get(account, account_id, section_id=section_id)
    _echo_response(ctx, response, AccountResponse)


@accounts_app.command("exists")
def accounts_exists(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    account_id: Annotated[str, typer.Argument(help="Account ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.exists(account, account_id, section_id=section_id)
    _echo_response(ctx, response, AccountExistenceResponse)


@accounts_app.command("create")
def accounts_create(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    title: Annotated[str, typer.Option("--title", help="Account title.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.create(
            account,
            section_id=section_id,
            title=title,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, AccountResponse)


@accounts_app.command("update")
def accounts_update(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    account_id: Annotated[str, typer.Argument(help="Account ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.update(
            account,
            account_id,
            section_id=section_id,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, AccountResponse)


@accounts_app.command("delete")
def accounts_delete(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    account_id: Annotated[str, typer.Argument(help="Account ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.delete(account, account_id, section_id=section_id)
    _echo_response(ctx, response, WhooingEnvelope)


@accounts_app.command("sort")
def accounts_sort(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    account_id: Annotated[list[str], typer.Argument(help="Account IDs in desired order.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.accounts.sort(account, section_id=section_id, account_ids=account_id)
    _echo_response(ctx, response, WhooingEnvelope)


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
    _echo_response(ctx, response, EntriesListResponse)


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
    _echo_response(ctx, response, EntriesResponse)


@entries_app.command("get")
def entries_get(
    ctx: typer.Context,
    entry_id: Annotated[str, typer.Argument(help="Entry ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.get(entry_id, section_id=section_id)
    _echo_response(ctx, response, EntryResponse)


@entries_app.command("create")
def entries_create(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.create(section_id=section_id, **_parse_fields(field))
    _echo_response(ctx, response, EntryResponse)


@entries_app.command("update")
def entries_update(
    ctx: typer.Context,
    entry_id: Annotated[str, typer.Argument(help="Entry ID.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.update(entry_id, section_id=section_id, **_parse_fields(field))
    _echo_response(ctx, response, EntryResponse)


@entries_app.command("update-many")
def entries_update_many(
    ctx: typer.Context,
    entry_id: Annotated[list[str], typer.Argument(help="Entry IDs.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.update_many(
            entry_id,
            section_id=section_id,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, EntriesResponse)


@entries_app.command("delete")
def entries_delete(
    ctx: typer.Context,
    entry_id: Annotated[list[str], typer.Argument(help="Entry IDs.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.delete(entry_id, section_id=section_id)
    _echo_response(ctx, response, WhooingEnvelope)


@entries_app.command("latest-items")
def entries_latest_items(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.latest_items(section_id=section_id)
    _echo_response(ctx, response, EntryNameAmountResponse)


@entries_app.command("analytics")
def entries_analytics(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Analytics endpoint name.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.analytics(name, section_id=section_id, **_parse_fields(param))
    _echo_response(ctx, response, _entry_analytics_model(name))


@entries_app.command("parse-outside")
def entries_parse_outside(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    rows: Annotated[str, typer.Option("--rows", help="Outside entry rows.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.parse_outside(section_id=section_id, rows=rows)
    _echo_response(ctx, response, EntriesResponse)


@entries_app.command("report-outside-source")
def entries_report_outside_source(
    ctx: typer.Context,
    source: Annotated[str, typer.Option("--source", help="Outside parser source.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.entries.report_outside_source(source)
    _echo_response(ctx, response, WhooingEnvelope)


@budgets_app.command("get")
def budgets_get(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.get(account, section_id=section_id, **_parse_fields(param))
    _echo_response(ctx, response, BudgetsResponse)


@budgets_app.command("update")
def budgets_update(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    target_ym: Annotated[str, typer.Option("--target-ym", help="Target year-month.")],
    amount: Annotated[
        list[str],
        typer.Option("--amount", "-a", help="Budget amount as account_id=amount. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.update(
            account,
            section_id=section_id,
            target_ym=target_ym,
            budgets=_parse_number_map(amount),
        )
    _echo_response(ctx, response, BudgetReportResponse)


@budgets_app.command("update-basic-total")
def budgets_update_basic_total(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    start_date: Annotated[str, typer.Option("--start-date", help="Start date.")],
    end_date: Annotated[str, typer.Option("--end-date", help="End date.")],
    month: Annotated[
        list[str],
        typer.Option("--month", "-m", help="Monthly total as yyyymm=amount. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.update_basic_total(
            account,
            section_id=section_id,
            start_date=start_date,
            end_date=end_date,
            monthly_totals={int(key): value for key, value in _parse_number_map(month).items()},
        )
    _echo_response(ctx, response, BudgetReportResponse)


@budgets_app.command("delete")
def budgets_delete(
    ctx: typer.Context,
    account: Annotated[str, typer.Argument(help="Account group.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    start_date: Annotated[str, typer.Option("--start-date", help="Start date.")],
    end_date: Annotated[str, typer.Option("--end-date", help="End date.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.delete(
            account,
            section_id=section_id,
            start_date=start_date,
            end_date=end_date,
        )
    _echo_response(ctx, response, WhooingEnvelope)


@budgets_app.command("goal")
def budgets_goal(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.get_goal(section_id=section_id, **_parse_fields(param))
    _echo_response(ctx, response, BudgetGoalResponse)


@budgets_app.command("update-goal")
def budgets_update_goal(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.update_goal(section_id=section_id, **_parse_fields(field))
    _echo_response(ctx, response, BudgetGoalResponse)


@budgets_app.command("delete-goal")
def budgets_delete_goal(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.delete_goal(section_id=section_id)
    _echo_response(ctx, response, WhooingEnvelope)


@budgets_app.command("capital-goal")
def budgets_capital_goal(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.budgets.get_capital_goal(section_id=section_id, **_parse_fields(param))
    _echo_response(ctx, response, CapitalGoalResponse)


@budgets_app.command("update-capital-goal")
def budgets_update_capital_goal(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    month: Annotated[
        list[str],
        typer.Option("--month", "-m", help="Capital goal as yyyymm=amount. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        monthly_goals = cast(Mapping[int | str, int | float], _parse_number_map(month))
        response = client.budgets.update_capital_goal(
            section_id=section_id,
            monthly_goals=monthly_goals,
        )
    _echo_response(ctx, response, CapitalGoalResponse)


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
    _echo_response(ctx, response, ReportResponse)


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
    _echo_response(ctx, response, ReportSummaryResponse)


@reports_app.command("custom-rows")
def reports_custom_rows(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    report: Annotated[
        Literal["report_bs", "report_pl"],
        typer.Option("--report", help="Report type."),
    ],
    action: Annotated[
        Literal["list", "info"],
        typer.Option("--action", help="Custom report action."),
    ] = "list",
    custom_id: Annotated[str | None, typer.Option("--custom-id", help="Custom row ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.reports.custom_rows(
            section_id=section_id,
            report=report,
            action=action,
            custom_id=custom_id,
            **_parse_fields(param),
        )
    _echo_response(ctx, response, CustomReportRowsResponse)


@reports_app.command("update-custom-rows")
def reports_update_custom_rows(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    report: Annotated[
        Literal["report_bs", "report_pl"],
        typer.Option("--report", help="Report type."),
    ],
    action: Annotated[
        Literal["post", "delete", "sort", "clean_disabled"],
        typer.Option("--action", help="Custom report action."),
    ],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.reports.update_custom_rows(
            section_id=section_id,
            report=report,
            action=action,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, ReportsListResponse)


@extras_app.command("frequent-items")
def extras_frequent_items(
    ctx: typer.Context,
    slot: Annotated[str | None, typer.Option("--slot", help="Frequent item slot.")] = None,
    item_id: Annotated[str | None, typer.Option("--item-id", help="Frequent item ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.frequent_items(slot, item_id, **_parse_fields(param))
    model = FrequentItemsSlotsResponse if slot is None else FrequentItemsResponse
    _echo_response(ctx, response, model)


@extras_app.command("create-frequent-item")
def extras_create_frequent_item(
    ctx: typer.Context,
    slot: Annotated[str, typer.Argument(help="Frequent item slot.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    item: Annotated[str, typer.Option("--item", help="Item name.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.create_frequent_item(
            slot,
            section_id=section_id,
            item=item,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, FrequentItemsResponse)


@extras_app.command("update-frequent-item")
def extras_update_frequent_item(
    ctx: typer.Context,
    slot: Annotated[str, typer.Argument(help="Frequent item slot.")],
    item_id: Annotated[str, typer.Argument(help="Frequent item ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.update_frequent_item(slot, item_id, **_parse_fields(field))
    _echo_response(ctx, response, FrequentItemsResponse)


@extras_app.command("delete-frequent-item")
def extras_delete_frequent_item(
    ctx: typer.Context,
    slot: Annotated[str, typer.Argument(help="Frequent item slot.")],
    item_id: Annotated[list[str], typer.Argument(help="Frequent item IDs.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_frequent_item(slot, item_id, section_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("sort-frequent-items")
def extras_sort_frequent_items(
    ctx: typer.Context,
    slot: Annotated[str, typer.Argument(help="Frequent item slot.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    item_id: Annotated[list[str], typer.Argument(help="Frequent item IDs in desired order.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.sort_frequent_items(slot, section_id=section_id, item_ids=item_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("monthly-items")
def extras_monthly_items(
    ctx: typer.Context,
    slot: Annotated[str | None, typer.Option("--slot", help="Monthly item slot.")] = None,
    item_id: Annotated[str | None, typer.Option("--item-id", help="Monthly item ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.monthly_items(item_id, slot=slot, **_parse_fields(param))
    model = MonthlyItemsResponse if slot is None and item_id is None else MonthlyItemsListResponse
    _echo_response(ctx, response, model)


@extras_app.command("create-monthly-item")
def extras_create_monthly_item(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    item: Annotated[str, typer.Option("--item", help="Item name.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.create_monthly_item(
            section_id=section_id,
            item=item,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, MonthlyItemsListResponse)


@extras_app.command("update-monthly-item")
def extras_update_monthly_item(
    ctx: typer.Context,
    item_id: Annotated[str, typer.Argument(help="Monthly item ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.update_monthly_item(item_id, **_parse_fields(field))
    _echo_response(ctx, response, MonthlyItemsListResponse)


@extras_app.command("delete-monthly-item")
def extras_delete_monthly_item(
    ctx: typer.Context,
    item_id: Annotated[list[str], typer.Argument(help="Monthly item IDs.")],
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_monthly_item(item_id, section_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("bill")
def extras_bill(
    ctx: typer.Context,
    account_id: Annotated[str | None, typer.Option("--account-id", help="Account ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.bill(account_id, **_parse_fields(param))
    _echo_response(ctx, response, BillsListResponse if account_id is None else BillsResponse)


@extras_app.command("checkcard")
def extras_checkcard(
    ctx: typer.Context,
    account_id: Annotated[str | None, typer.Option("--account-id", help="Account ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.checkcard(account_id, **_parse_fields(param))
    model = CheckcardsListResponse if account_id is None else CheckcardsResponse
    _echo_response(ctx, response, model)


@extras_app.command("in-out")
def extras_in_out(
    ctx: typer.Context,
    account: Annotated[str | None, typer.Option("--account", help="Account group.")] = None,
    account_id: Annotated[str | None, typer.Option("--account-id", help="Account ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.in_out(account, account_id, **_parse_fields(param))
    if account is None:
        model: PydanticModel[object] = InOutListResponse
    elif account_id is None:
        model = InOutResponse
    else:
        model = InOutAccountResponse
    _echo_response(ctx, response, model)


@extras_app.command("calendar")
def extras_calendar(
    ctx: typer.Context,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.calendar(**_parse_fields(param))
    _echo_response(ctx, response, CalendarResponse)


@extras_app.command("post-its")
def extras_post_its(
    ctx: typer.Context,
    post_it_id: Annotated[str | None, typer.Option("--post-it-id", help="Post-it ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.post_its(post_it_id, **_parse_fields(param))
    _echo_response(ctx, response, PostItsResponse if post_it_id is None else PostItResponse)


@extras_app.command("create-post-it")
def extras_create_post_it(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    title: Annotated[str, typer.Option("--title", help="Post-it title.")],
    contents: Annotated[str, typer.Option("--contents", help="Post-it contents.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.create_post_it(
            section_id=section_id,
            title=title,
            contents=contents,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, PostItResponse)


@extras_app.command("update-post-it")
def extras_update_post_it(
    ctx: typer.Context,
    post_it_id: Annotated[str, typer.Argument(help="Post-it ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.update_post_it(post_it_id, **_parse_fields(field))
    _echo_response(ctx, response, PostItResponse)


@extras_app.command("delete-post-it")
def extras_delete_post_it(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Option("--section-id", help="Section ID.")],
    post_it_id: Annotated[list[str], typer.Argument(help="Post-it IDs.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_post_it(section_id, post_it_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("messages")
def extras_messages(
    ctx: typer.Context,
    opponent_user_id: Annotated[
        str | None,
        typer.Option("--opponent-user-id", help="Opponent user ID."),
    ] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.messages(opponent_user_id, **_parse_fields(param))
    _echo_response(ctx, response, MessagesResponse)


@extras_app.command("send-message")
def extras_send_message(
    ctx: typer.Context,
    opponent_user_id: Annotated[list[str], typer.Option("--opponent-user-id", help="User ID.")],
    message: Annotated[str, typer.Option("--message", help="Message body.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.send_message(
            opponent_user_ids=opponent_user_id,
            message=message,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, MessagesResponse)


@extras_app.command("delete-messages")
def extras_delete_messages(
    ctx: typer.Context,
    opponent_user_id: Annotated[str, typer.Argument(help="Opponent user ID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_messages(opponent_user_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("unread-messages")
def extras_unread_messages(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.unread_messages()
    _echo_response(ctx, response, UnreadMessagesResponse)


@extras_app.command("bbs")
def extras_bbs(
    ctx: typer.Context,
    category: Annotated[str | None, typer.Option("--category", help="BBS category.")] = None,
    bbs_id: Annotated[str | None, typer.Option("--bbs-id", help="BBS post ID.")] = None,
    comment_id: Annotated[str | None, typer.Option("--comment-id", help="Comment ID.")] = None,
    param: Annotated[
        list[str] | None,
        typer.Option("--param", "-p", help="Query parameter as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.bbs(category, bbs_id, comment_id, **_parse_fields(param))
    if comment_id is not None:
        model: PydanticModel[object] = BbsCommentsResponse
    elif bbs_id is not None:
        model = BbsPostResponse
    else:
        model = BbsPostsResponse
    _echo_response(ctx, response, model)


@extras_app.command("create-bbs")
def extras_create_bbs(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    title: Annotated[str, typer.Option("--title", help="BBS title.")],
    contents: Annotated[str, typer.Option("--contents", help="BBS contents.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.create_bbs(
            category,
            title=title,
            contents=contents,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, BbsPostResponse)


@extras_app.command("update-bbs")
def extras_update_bbs(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[str, typer.Argument(help="BBS post ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.update_bbs(category, bbs_id, **_parse_fields(field))
    _echo_response(ctx, response, BbsPostResponse)


@extras_app.command("delete-bbs")
def extras_delete_bbs(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[list[str], typer.Argument(help="BBS post IDs.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_bbs(category, bbs_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("create-bbs-comment")
def extras_create_bbs_comment(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[str, typer.Argument(help="BBS post ID.")],
    contents: Annotated[str, typer.Option("--contents", help="Comment contents.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.create_bbs_comment(
            category,
            bbs_id,
            contents=contents,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, BbsCommentsResponse)


@extras_app.command("update-bbs-comment")
def extras_update_bbs_comment(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[str, typer.Argument(help="BBS post ID.")],
    comment_id: Annotated[str, typer.Argument(help="Comment ID.")],
    field: Annotated[
        list[str],
        typer.Option("--field", "-f", help="Form field as key=value. Repeatable."),
    ],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.update_bbs_comment(
            category,
            bbs_id,
            comment_id,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, BbsCommentsResponse)


@extras_app.command("delete-bbs-comment")
def extras_delete_bbs_comment(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[str, typer.Argument(help="BBS post ID.")],
    comment_id: Annotated[list[str], typer.Argument(help="Comment IDs.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_bbs_comment(category, bbs_id, comment_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("create-bbs-reply")
def extras_create_bbs_reply(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[str, typer.Argument(help="BBS post ID.")],
    comment_id: Annotated[str, typer.Argument(help="Comment ID.")],
    contents: Annotated[str, typer.Option("--contents", help="Reply contents.")],
    field: Annotated[
        list[str] | None,
        typer.Option("--field", "-f", help="Additional form field as key=value. Repeatable."),
    ] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.create_bbs_reply(
            category,
            bbs_id,
            comment_id,
            contents=contents,
            **_parse_fields(field),
        )
    _echo_response(ctx, response, BbsCommentsResponse)


@extras_app.command("delete-bbs-reply")
def extras_delete_bbs_reply(
    ctx: typer.Context,
    category: Annotated[str, typer.Argument(help="BBS category.")],
    bbs_id: Annotated[str, typer.Argument(help="BBS post ID.")],
    comment_id: Annotated[str, typer.Argument(help="Comment ID.")],
    addition_id: Annotated[list[str], typer.Argument(help="Reply addition IDs.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.delete_bbs_reply(category, bbs_id, comment_id, addition_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("recommend-bbs")
def extras_recommend_bbs(
    ctx: typer.Context,
    bbs_id: Annotated[str, typer.Option("--bbs-id", help="BBS post ID.")],
    comment_id: Annotated[str | None, typer.Option("--comment-id", help="Comment ID.")] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.recommend_bbs(bbs_id=bbs_id, comment_id=comment_id)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("prepare-upload")
def extras_prepare_upload(
    ctx: typer.Context,
    name: Annotated[str, typer.Option("--name", help="File name.")],
    mime_type: Annotated[str, typer.Option("--mime-type", help="File MIME type.")],
    size: Annotated[int, typer.Option("--size", help="File size in bytes.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.prepare_upload(name=name, mime_type=mime_type, size=size)
    _echo_response(ctx, response, UploadInfoResponse)


@extras_app.command("complete-upload")
def extras_complete_upload(
    ctx: typer.Context,
    uuid: Annotated[str, typer.Argument(help="Prepared upload UUID.")],
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.complete_upload(uuid)
    _echo_response(ctx, response, WhooingEnvelope)


@extras_app.command("notifications")
def extras_notifications(
    ctx: typer.Context,
    section_id: Annotated[str | None, typer.Option("--section-id", help="Section ID.")] = None,
) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.notifications(section_id=section_id)
    _echo_response(ctx, response, NotificationsResponse)


@extras_app.command("mark-notifications-read")
def extras_mark_notifications_read(ctx: typer.Context) -> None:
    with _client_from_state(_state(ctx)) as client:
        response = client.extras.mark_notifications_read()
    _echo_response(ctx, response, WhooingEnvelope)


@profile_app.command("set")
def profile_set(
    ctx: typer.Context,
    api_key: Annotated[str | None, typer.Option("--api-key", help="Whooing API key.")] = None,
    access_token: Annotated[
        str | None,
        typer.Option("--access-token", help="OAuth bearer access token."),
    ] = None,
) -> None:
    resolved_api_key, resolved_access_token = _profile_credentials(
        api_key=api_key,
        access_token=access_token,
    )
    state = _state(ctx)
    config = set_profile(
        load_config(state.config_path),
        name=state.profile,
        api_key=resolved_api_key,
        access_token=resolved_access_token,
    )
    save_config(state.config_path, config)
    _echo_payload(ctx, {"profile": state.profile, "saved": True})


@profile_app.command("show")
def profile_show(ctx: typer.Context) -> None:
    state = _state(ctx)
    profile = load_config(state.config_path).profiles.get(state.profile)
    if profile is None:
        raise ClickException(f"Profile not found: {state.profile}")
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


def _echo_payload_model(
    ctx: typer.Context,
    payload: JsonObject,
    model: PydanticModel[object],
) -> None:
    model.model_validate(payload)
    _echo_payload(ctx, payload)


def _echo_response(
    ctx: typer.Context,
    response: ApiResponse[JsonValue],
    model: PydanticModel[object],
) -> None:
    model.model_validate(response.raw)
    _echo_payload(ctx, response.raw)


@contextmanager
def _client_from_state(state: CliState) -> Iterator[WhooingClient]:
    auth_kwargs = _auth_kwargs(state)
    with WhooingClient(base_url=state.base_url, **auth_kwargs) as client:
        yield client


def _profile_credentials(
    *,
    api_key: str | None,
    access_token: str | None,
) -> tuple[str | None, str | None]:
    if api_key is not None or access_token is not None:
        return api_key, access_token

    env_api_key = os.environ.get("WHOOING_API_KEY")
    env_access_token = os.environ.get("WHOOING_ACCESS_TOKEN")
    if env_api_key is not None and env_access_token is not None:
        raise ClickException("Set only one of WHOOING_API_KEY or WHOOING_ACCESS_TOKEN.")
    if env_api_key is not None:
        return env_api_key, None
    if env_access_token is not None:
        return None, env_access_token

    raise ClickException(
        "Provide --api-key, --access-token, WHOOING_API_KEY, or WHOOING_ACCESS_TOKEN."
    )


def _auth_kwargs(state: CliState) -> _ClientAuthKwargs:
    if state.api_key is not None and state.access_token is not None:
        raise ClickException("Provide only one of --api-key or --access-token.")
    if state.api_key is not None:
        return {"api_key": state.api_key}
    if state.access_token is not None:
        return {"access_token": state.access_token}

    env_api_key = os.environ.get("WHOOING_API_KEY")
    env_access_token = os.environ.get("WHOOING_ACCESS_TOKEN")
    if env_api_key is not None and env_access_token is not None:
        raise ClickException("Set only one of WHOOING_API_KEY or WHOOING_ACCESS_TOKEN.")
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

    raise ClickException(
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
    return _validate_request_data(data)


def _parse_fields(values: list[str] | None) -> dict[str, RequestValue]:
    return dict(_parse_pairs(values) or {})


def _parse_number_map(values: list[str]) -> dict[str, int | float]:
    data: dict[str, int | float] = {}
    for value in values:
        key, separator, raw = value.partition("=")
        if not separator or not key:
            raise typer.BadParameter(f"Expected key=number: {value}")
        parsed = _parse_request_value(raw)
        if not isinstance(parsed, int | float) or isinstance(parsed, bool):
            raise typer.BadParameter(f"Expected numeric value: {value}")
        data[key] = parsed
    return data


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


def _validate_request_data(data: dict[str, RequestValue]) -> dict[str, RequestValue]:
    return RequestDataAdapter.validate_python(data)


def _entry_analytics_model(name: str) -> PydanticModel[object]:
    models: dict[str, PydanticModel[object]] = {
        "flow_of_account": EntryFlowResponse,
        "flow_of_account_id": EntryFlowResponse,
        "changes_of_account_id": EntryChangeResponse,
        "changes_of_client": EntryChangeResponse,
        "changes_of_item": EntryChangeResponse,
        "account_ids_of_account": EntryNameAmountResponse,
        "clients_of_account_id": EntryNameAmountResponse,
        "items_of_account_id": EntryNameAmountResponse,
    }
    return models.get(name, EntryAnalysisResponse)


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
