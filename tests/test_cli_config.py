from __future__ import annotations

import stat
from pathlib import Path

import pytest

from whooing.cli_config import (
    CliConfig,
    CliProfile,
    load_config,
    save_config,
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
    config = CliConfig(profiles={"default": CliProfile(access_token="old-token")})

    updated = set_profile(config, name="default", api_key="new-key")

    assert updated.profiles["default"] == CliProfile(api_key="new-key")


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
