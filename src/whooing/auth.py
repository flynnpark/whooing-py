from __future__ import annotations

import base64
import hashlib
import secrets
import time
from collections.abc import Iterable
from dataclasses import dataclass
from urllib.parse import urlencode

from whooing.types import Headers


class Auth:
    def headers(self) -> Headers:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class APIKeyAuth(Auth):
    api_key: str

    def headers(self) -> Headers:
        return {"X-API-KEY": self.api_key}


@dataclass(frozen=True, slots=True)
class BearerTokenAuth(Auth):
    access_token: str

    def headers(self) -> Headers:
        return {"Authorization": f"Bearer {self.access_token}"}


@dataclass(frozen=True, slots=True)
class OAuth1aAuth(Auth):
    app_id: str
    app_secret: str
    token: str
    token_secret: str

    def headers(self) -> Headers:
        signature = hashlib.sha1(f"{self.app_secret}|{self.token_secret}".encode()).hexdigest()
        nonce = secrets.token_hex(20)
        timestamp = str(int(time.time()))
        value = ",".join(
            (
                f"app_id={self.app_id}",
                f"token={self.token}",
                f"signature={signature}",
                f"nounce={nonce}",
                f"timestamp={timestamp}",
            )
        )
        return {"X-API-KEY": value}


@dataclass(frozen=True, slots=True)
class PKCEChallenge:
    verifier: str
    challenge: str
    method: str = "S256"


def create_pkce_challenge(byte_length: int = 64) -> PKCEChallenge:
    verifier = secrets.token_urlsafe(byte_length)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return PKCEChallenge(verifier=verifier, challenge=challenge)


def build_authorization_url(
    *,
    client_id: str,
    redirect_uri: str,
    scopes: Iterable[str] = (),
    state: str | None = None,
    challenge: PKCEChallenge | None = None,
    authorization_endpoint: str = "https://whooing.com/oauth2/authorize",
) -> str:
    params: dict[str, str] = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    scope_value = ",".join(scopes)
    if scope_value:
        params["scope"] = scope_value
    if state is not None:
        params["state"] = state
    if challenge is not None:
        params["code_challenge"] = challenge.challenge
        params["code_challenge_method"] = challenge.method
    return f"{authorization_endpoint}?{urlencode(params)}"
