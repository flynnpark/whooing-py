from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from whooing import WhooingClient

pytestmark = pytest.mark.integration
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        pytest.skip(f"{name} 환경 변수가 필요합니다.")
    return value


def test_real_user_and_sections_api() -> None:
    api_key = require_env("WHOOING_API_KEY")

    with WhooingClient(api_key=api_key) as client:
        user = client.users.get()
        sections = client.sections.list()

    assert user.code == 200
    assert sections.code == 200


def test_real_entries_latest_api() -> None:
    api_key = require_env("WHOOING_API_KEY")
    section_id = require_env("WHOOING_SECTION_ID")

    with WhooingClient(api_key=api_key) as client:
        response = client.entries.latest(section_id=section_id)

    assert response.code == 200
