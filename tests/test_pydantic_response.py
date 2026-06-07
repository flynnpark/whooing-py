from __future__ import annotations

from pydantic import BaseModel

from whooing.response import parse_api_response


class Section(BaseModel):
    section_id: str
    title: str


class SectionsResponse(BaseModel):
    code: int
    rest_of_api: int
    results: list[Section]


def test_parse_response_with_pydantic_model() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "rest_of_api": 10,
            "error_parameters": {},
            "results": [{"section_id": "s1", "title": "개인"}],
        }
    )

    parsed = response.parse(SectionsResponse)

    assert parsed.results[0].section_id == "s1"


def test_parse_results_with_pydantic_model() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "rest_of_api": 10,
            "error_parameters": {},
            "results": {"section_id": "s1", "title": "개인"},
        }
    )

    parsed = response.parse_results(Section)

    assert parsed.title == "개인"


def test_parse_results_as_supports_collection_annotations() -> None:
    response = parse_api_response(
        {
            "code": 200,
            "message": "",
            "rest_of_api": 10,
            "error_parameters": {},
            "results": [{"section_id": "s1", "title": "개인"}],
        }
    )

    parsed = response.parse_results_as(list[Section])

    assert isinstance(parsed, list)
    assert parsed[0].section_id == "s1"
