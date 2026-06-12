from __future__ import annotations

from whooing._pydantic_models.base import WhooingModel


class OAuthErrorResponse(WhooingModel):
    error: str
    error_description: str | None = None


class OAuth2TokenResponse(WhooingModel):
    access_token: str
    token_type: str
    expires_in: int | None = None
    refresh_token: str | None = None
    scope: str | None = None


class OAuth2MetadataResponse(WhooingModel):
    issuer: str | None = None
    authorization_endpoint: str
    token_endpoint: str
    revocation_endpoint: str | None = None
    response_types_supported: list[str] | None = None
    grant_types_supported: list[str] | None = None
    code_challenge_methods_supported: list[str] | None = None
    scopes_supported: list[str] | None = None


class OAuth1RequestTokenResponse(WhooingModel):
    token: str


class OAuth1AccessTokenResponse(WhooingModel):
    token: str
    token_secret: str
    user_id: int | None = None
