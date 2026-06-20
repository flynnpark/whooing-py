from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import httpx

RetryStatusCode = Literal[429, 500, 502, 503, 504]


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0
    retry_status_codes: frozenset[RetryStatusCode] = frozenset({429, 500, 502, 503, 504})
    respect_retry_after: bool = True

    def should_retry(self, response: httpx.Response, attempt: int) -> bool:
        return attempt < self.max_attempts and response.status_code in self.retry_status_codes

    def delay_for(self, response: httpx.Response, attempt: int) -> float:
        if self.respect_retry_after:
            retry_after = parse_retry_after(response.headers.get("Retry-After"))
            if retry_after is not None:
                return retry_after
        return self.backoff_seconds * attempt


def parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        delay = float(value)
    except ValueError:
        return None
    if delay < 0:
        return None
    return delay
