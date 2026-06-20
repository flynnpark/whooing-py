from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping

from whooing.exceptions import (
    WhooingAPIError,
    WhooingError,
    WhooingOAuthError,
    WhooingRateLimitError,
    WhooingResponseError,
    WhooingTransportError,
)
from whooing.types import JsonObject, JsonValue

OutputFormat = str


def render_output(value: JsonValue, output_format: OutputFormat) -> str:
    if output_format == "json":
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    if output_format == "table":
        return _render_table(value)
    if output_format == "csv":
        return _render_csv(value)
    msg = f"Unsupported output format: {output_format}"
    raise ValueError(msg)


def render_error(exc: WhooingError) -> JsonObject:
    payload: JsonObject = {"error": exc.__class__.__name__, "message": str(exc)}
    if isinstance(exc, WhooingAPIError):
        payload["code"] = exc.code
        payload["rest_of_api"] = exc.rest_of_api
        payload["http_status_code"] = exc.http_status_code
        payload["error_parameters"] = exc.error_parameters
    if isinstance(exc, WhooingRateLimitError):
        payload["retry_after"] = exc.retry_after
    if isinstance(exc, WhooingResponseError):
        payload["status_code"] = exc.status_code
        payload["body"] = exc.body
    if isinstance(exc, WhooingOAuthError):
        payload["oauth_error"] = exc.error
        payload["description"] = exc.description
    if isinstance(exc, WhooingTransportError):
        payload["transport_error"] = True
    return payload


def _render_table(value: JsonValue) -> str:
    rows = _rows(value)
    if not rows:
        return ""
    columns = _columns(rows)
    widths = {
        column: max(len(column), *(len(_cell(row.get(column))) for row in rows))
        for column in columns
    }
    lines = [
        "  ".join(column.ljust(widths[column]) for column in columns),
        "  ".join("-" * widths[column] for column in columns),
    ]
    lines.extend(
        "  ".join(_cell(row.get(column)).ljust(widths[column]) for column in columns)
        for row in rows
    )
    return "\n".join(lines)


def _render_csv(value: JsonValue) -> str:
    rows = _rows(value)
    if not rows:
        return ""
    columns = _columns(rows)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: _cell(row.get(column)) for column in columns})
    return buffer.getvalue().rstrip("\r\n")


def _rows(value: JsonValue) -> list[JsonObject]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        results = value.get("results")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]
        if isinstance(results, dict):
            return [results]
        return [value]
    return [{"value": value}]


def _columns(rows: list[JsonObject]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    return columns


def _cell(value: JsonValue | Mapping[str, JsonValue]) -> str:
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if value is None:
        return ""
    return str(value)
