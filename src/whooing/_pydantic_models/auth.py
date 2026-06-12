from __future__ import annotations

from typing import Annotated

from pydantic import Field

from whooing._pydantic_models.base import WhooingModel


class OAuthErrorResponse(WhooingModel):
    error: Annotated[str, Field(title="OAuth 오류 코드", description="OAuth 인증 실패 코드입니다.")]
    error_description: Annotated[
        str | None,
        Field(title="OAuth 오류 설명", description="OAuth 인증 실패에 대한 상세 설명입니다."),
    ] = None


class OAuth2TokenResponse(WhooingModel):
    access_token: Annotated[
        str,
        Field(title="액세스 토큰", description="후잉 OAuth2 API 호출에 사용할 액세스 토큰입니다."),
    ]
    token_type: Annotated[
        str,
        Field(title="토큰 타입", description="OAuth2 토큰 타입입니다. 일반적으로 Bearer입니다."),
    ]
    expires_in: Annotated[
        int | None,
        Field(
            title="만료까지 남은 시간", description="액세스 토큰 만료까지 남은 초 단위 시간입니다."
        ),
    ] = None
    refresh_token: Annotated[
        str | None,
        Field(title="리프레시 토큰", description="액세스 토큰 갱신에 사용할 토큰입니다."),
    ] = None
    scope: Annotated[
        str | None,
        Field(title="권한 범위", description="OAuth2 토큰에 부여된 권한 범위입니다."),
    ] = None


class OAuth2MetadataResponse(WhooingModel):
    issuer: Annotated[
        str | None,
        Field(title="발급자", description="OAuth2 메타데이터의 토큰 발급자입니다."),
    ] = None
    authorization_endpoint: Annotated[
        str,
        Field(
            title="인가 엔드포인트", description="사용자 인가를 요청하는 OAuth2 엔드포인트입니다."
        ),
    ]
    token_endpoint: Annotated[
        str,
        Field(
            title="토큰 엔드포인트",
            description="인가 코드를 토큰으로 교환하는 OAuth2 엔드포인트입니다.",
        ),
    ]
    revocation_endpoint: Annotated[
        str | None,
        Field(
            title="토큰 폐기 엔드포인트",
            description="토큰 폐기를 요청하는 OAuth2 엔드포인트입니다.",
        ),
    ] = None
    response_types_supported: Annotated[
        list[str] | None,
        Field(
            title="지원 응답 타입", description="OAuth2 서버가 지원하는 response_type 목록입니다."
        ),
    ] = None
    grant_types_supported: Annotated[
        list[str] | None,
        Field(title="지원 Grant 타입", description="OAuth2 서버가 지원하는 grant_type 목록입니다."),
    ] = None
    code_challenge_methods_supported: Annotated[
        list[str] | None,
        Field(
            title="지원 PKCE 방식",
            description="OAuth2 PKCE에서 지원하는 code_challenge 방식 목록입니다.",
        ),
    ] = None
    scopes_supported: Annotated[
        list[str] | None,
        Field(title="지원 권한 범위", description="OAuth2 서버가 지원하는 scope 목록입니다."),
    ] = None


class OAuth1RequestTokenResponse(WhooingModel):
    token: Annotated[
        str,
        Field(
            title="요청 토큰", description="후잉 App 인증 승인 URL 생성에 사용하는 요청 토큰입니다."
        ),
    ]


class OAuth1AccessTokenResponse(WhooingModel):
    token: Annotated[
        str,
        Field(
            title="액세스 토큰", description="후잉 App 인증 API 호출에 사용할 액세스 토큰입니다."
        ),
    ]
    token_secret: Annotated[
        str,
        Field(title="토큰 시크릿", description="OAuth1a 서명 생성에 사용하는 토큰 시크릿입니다."),
    ]
    user_id: Annotated[
        int | None,
        Field(title="사용자 ID", description="토큰과 연결된 후잉 사용자 식별자입니다."),
    ] = None
