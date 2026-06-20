from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from whooing.types import JsonObject


@dataclass(frozen=True, slots=True)
class CliProfile:
    api_key: str | None = None
    access_token: str | None = None

    def to_json(self) -> JsonObject:
        data: JsonObject = {}
        if self.api_key is not None:
            data["api_key"] = self.api_key
        if self.access_token is not None:
            data["access_token"] = self.access_token
        return data


@dataclass(frozen=True, slots=True)
class CliConfig:
    profiles: dict[str, CliProfile]

    def to_json(self) -> JsonObject:
        return {"profiles": {name: profile.to_json() for name, profile in self.profiles.items()}}


def default_config_path() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "whooing-py" / "config.json"
    return Path.home() / ".config" / "whooing-py" / "config.json"


def load_config(path: Path) -> CliConfig:
    if not path.exists():
        return CliConfig(profiles={})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = "CLI config must be a JSON object."
        raise ValueError(msg)
    profiles_value = payload.get("profiles", {})
    if not isinstance(profiles_value, dict):
        msg = "CLI config profiles must be a JSON object."
        raise ValueError(msg)
    profiles: dict[str, CliProfile] = {}
    for name, value in profiles_value.items():
        if not isinstance(name, str) or not isinstance(value, dict):
            continue
        api_key = value.get("api_key")
        access_token = value.get("access_token")
        profiles[name] = CliProfile(
            api_key=api_key if isinstance(api_key, str) else None,
            access_token=access_token if isinstance(access_token, str) else None,
        )
    return CliConfig(profiles=profiles)


def save_config(path: Path, config: CliConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(config.to_json(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def set_profile(
    config: CliConfig,
    *,
    name: str,
    api_key: str | None = None,
    access_token: str | None = None,
) -> CliConfig:
    current = config.profiles.get(name, CliProfile())
    profiles = dict(config.profiles)
    profiles[name] = CliProfile(
        api_key=api_key if api_key is not None else current.api_key,
        access_token=access_token if access_token is not None else current.access_token,
    )
    return CliConfig(profiles=profiles)


def remove_profile(config: CliConfig, *, name: str) -> CliConfig:
    profiles = dict(config.profiles)
    profiles.pop(name, None)
    return CliConfig(profiles=profiles)


def mask_secret(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"
