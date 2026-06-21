from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from whooing import WhooingClient
from whooing.exceptions import WhooingResponseError
from whooing.pydantic_models import (
    AccountsResponse,
    EntriesResponse,
    SectionsResponse,
    UserResponse,
)
from whooing.types import JsonValue

pytestmark = pytest.mark.integration
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        pytest.skip(f"{name} 환경 변수가 필요합니다.")
    return value


def skip_unavailable_api(exc: WhooingResponseError) -> None:
    if exc.status_code in {401, 403}:
        pytest.skip(f"후잉 API 인증 또는 권한 확인에 실패했습니다: HTTP {exc.status_code}")
    raise exc


def resolve_section_id(client: WhooingClient) -> str:
    configured = os.environ.get("WHOOING_SECTION_ID")
    if configured:
        return configured

    try:
        response = client.sections.list()
    except WhooingResponseError as exc:
        skip_unavailable_api(exc)
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

    try:
        with WhooingClient(api_key=api_key) as client:
            user = client.users.get()
            sections = client.sections.list()
    except WhooingResponseError as exc:
        skip_unavailable_api(exc)

    assert user.code == 200
    assert sections.code == 200

    parsed_user = user.parse(UserResponse)
    parsed_sections = sections.parse(SectionsResponse)

    assert parsed_user.results is not None
    assert parsed_sections.results is not None


def test_real_entries_latest_api() -> None:
    api_key = require_env("WHOOING_API_KEY")

    try:
        with WhooingClient(api_key=api_key) as client:
            section_id = resolve_section_id(client)
            response = client.entries.latest(section_id=section_id)
    except WhooingResponseError as exc:
        skip_unavailable_api(exc)

    assert response.code == 200

    parsed = response.parse(EntriesResponse)
    assert parsed.results is not None


def test_real_accounts_api_matches_pydantic_model() -> None:
    api_key = require_env("WHOOING_API_KEY")

    try:
        with WhooingClient(api_key=api_key) as client:
            section_id = resolve_section_id(client)
            response = client.accounts.list(section_id=section_id)
    except WhooingResponseError as exc:
        skip_unavailable_api(exc)

    assert response.code == 200

    parsed = response.parse(AccountsResponse)
    assert parsed.results is not None
