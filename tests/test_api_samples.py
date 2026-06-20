from __future__ import annotations

import json
from pathlib import Path

from whooing.pydantic_models import EntriesListResponse, NotificationsResponse, UserResponse
from whooing.response import parse_api_response
from whooing.types import JsonObject

SAMPLES_DIR = Path(__file__).parent / "fixtures" / "api_samples"


def load_sample(name: str) -> JsonObject:
    data = json.loads((SAMPLES_DIR / name).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"API sample must be a JSON object: {name}"
        raise TypeError(msg)
    return data


def test_user_sample_matches_response_model() -> None:
    parsed = parse_api_response(load_sample("user.json")).parse(UserResponse)

    assert parsed.results is not None
    assert parsed.results.username == "Helloman"
    assert parsed.results.timezone == "Asia/Seoul"


def test_entries_list_sample_matches_response_model() -> None:
    parsed = parse_api_response(load_sample("entries_list.json")).parse(EntriesListResponse)

    assert parsed.results is not None
    assert parsed.results.rows[0].entry_id == "e1"
    assert parsed.results.rows[0].attachments == []


def test_notifications_sample_matches_response_model_aliases() -> None:
    parsed = parse_api_response(load_sample("notifications.json")).parse(NotificationsResponse)

    assert parsed.results is not None
    assert parsed.results.new_releases == 0
    assert parsed.results.notification is not None
    assert parsed.results.notification.badge_count == 1
