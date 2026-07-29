from __future__ import annotations

import stat
from pathlib import Path

import pytest

from whooing.cli_config import (
    CliConfig,
    CliProfile,
    load_config,
    save_config,
    set_oauth_profile,
    set_profile,
)


def test_save_config_restricts_file_permissions(tmp_path: Path) -> None:
    config_path = tmp_path / "whooing-py" / "config.json"

    save_config(
        config_path,
        CliConfig(profiles={"default": CliProfile(api_key="secret")}),
    )

    assert stat.S_IMODE(config_path.stat().st_mode) == stat.S_IRUSR | stat.S_IWUSR


def test_set_profile_replaces_the_previous_authentication_method() -> None:
    config = CliConfig(
        profiles={"default": CliProfile(access_token="old-token", section_id="s123")}
    )

    updated = set_profile(config, name="default", api_key="new-key")

    assert updated.profiles["default"] == CliProfile(api_key="new-key", section_id="s123")


def test_set_profile_rejects_multiple_authentication_methods() -> None:
    with pytest.raises(ValueError, match="only one authentication method"):
        set_profile(
            CliConfig(profiles={}),
            name="default",
            api_key="key",
            access_token="token",
        )


def test_load_config_rejects_invalid_json_without_exposing_parser_details(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError, match="Unable to read CLI config"):
        load_config(config_path)


def test_set_profile_updates_section_without_replacing_oauth_tokens() -> None:
    profile = CliProfile(
        access_token="access",
        refresh_token="refresh",
        oauth_client_id="app",
        oauth_scope="read",
    )

    updated = set_profile(
        CliConfig(profiles={"default": profile}),
        name="default",
        section_id="s123",
    )

    assert updated.profiles["default"] == CliProfile(
        access_token="access",
        refresh_token="refresh",
        oauth_client_id="app",
        oauth_scope="read",
        section_id="s123",
    )


def test_set_oauth_profile_replaces_api_key_and_preserves_section() -> None:
    config = CliConfig(profiles={"default": CliProfile(api_key="old-key", section_id="s123")})

    updated = set_oauth_profile(
        config,
        name="default",
        access_token="access",
        refresh_token="refresh",
        client_id="app",
        scope="read,write",
        section_id=None,
    )

    assert updated.profiles["default"] == CliProfile(
        access_token="access",
        refresh_token="refresh",
        oauth_client_id="app",
        oauth_scope="read,write",
        section_id="s123",
    )
