from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from whooing import WhooingClient
from whooing.types import JsonValue

pytestmark = pytest.mark.integration
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        pytest.skip(f"{name} 환경 변수가 필요합니다.")
    return value


def resolve_section_id(client: WhooingClient) -> str:
    configured = os.environ.get("WHOOING_SECTION_ID")
    if configured:
        return configured

    response = client.sections.list()
    results = response.results
    if not isinstance(results, list):
        pytest.skip("섹션 목록 응답에서 section_id를 찾을 수 없습니다.")

    for section in results:
        section_id = _section_id_from(section)
        if section_id is not None:
            return section_id

    pytest.skip("사용 가능한 후잉 섹션이 없습니다.")


def _section_id_from(value: JsonValue) -> str | None:
    if not isinstance(value, dict):
        return None
    section_id = value.get("section_id")
    if isinstance(section_id, str) and section_id:
        return section_id
    return None


def test_real_user_and_sections_api() -> None:
    api_key = require_env("WHOOING_API_KEY")

    with WhooingClient(api_key=api_key) as client:
        user = client.users.get()
        sections = client.sections.list()

    assert user.code == 200
    assert sections.code == 200


def test_real_entries_latest_api() -> None:
    api_key = require_env("WHOOING_API_KEY")

    with WhooingClient(api_key=api_key) as client:
        section_id = resolve_section_id(client)
        response = client.entries.latest(section_id=section_id)

    assert response.code == 200
