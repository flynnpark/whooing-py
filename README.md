# whooing-py

[후잉 개발자 API](https://whooing.com/api/docs)를 위한 Python 클라이언트 라이브러리입니다.

## 상태

공식 문서 기준의 1차 클라이언트 구현이 들어간 상태입니다. 동기/비동기 클라이언트,
API key/Bearer/OAuth 1.0a 인증 헤더, OAuth 2.0 PKCE 토큰 헬퍼, 주요 API 리소스 호출
메서드, 응답 메타데이터와 오류 매핑을 제공합니다.

응답 스키마는 API 전역에서 폭이 넓기 때문에 현재는 `ApiResponse[JsonValue]` 형태로
`results`, `rest_of_api`, `code`, 원본 `raw`를 보존합니다. 자주 쓰는 도메인부터 별도
모델을 점진적으로 얹을 수 있는 구조입니다.

## 도구

- Python: `asdf`로 관리
- 패키지 및 환경 관리: `uv`
- 빌드 백엔드: `hatchling`
- 정적 분석: `ruff`, `mypy`
- 테스트: `pytest`

## 설정

```sh
asdf install
uv sync --dev
```

## 개발

```sh
uv run ruff check .
uv run mypy src
uv run pytest
```

## 사용 예시

API key 기반 동기 호출:

```python
from whooing import WhooingClient

with WhooingClient(api_key="발급된_인증키") as client:
    sections = client.sections.list()
    print(sections.rest_of_api)
    print(sections.results)
```

Bearer token 기반 비동기 호출:

```python
from whooing import AsyncWhooingClient

async with AsyncWhooingClient(access_token="access-token") as client:
    response = await client.entries.list(section_id="s123", limit=20)
    print(response.results)
```

OAuth 2.0 PKCE 토큰 교환:

```python
from whooing import OAuth2TokenClient
from whooing.auth import build_authorization_url, create_pkce_challenge

challenge = create_pkce_challenge()
url = build_authorization_url(
    client_id="app_id",
    redirect_uri="http://localhost/callback",
    scopes=["read", "write"],
    state="csrf-token",
    challenge=challenge,
)

with OAuth2TokenClient() as oauth:
    token = oauth.exchange_code(
        client_id="app_id",
        code="callback-code",
        redirect_uri="http://localhost/callback",
        code_verifier=challenge.verifier,
    )
```

## 리소스 구성

- `client.users`: 사용자 정보, 사용자 로그, 포인트 로그
- `client.sections`: 섹션 조회/생성/수정/삭제/정렬
- `client.accounts`: 항목 조회/생성/수정/삭제/정렬
- `client.entries`: 거래 조회/입력/수정/삭제, 최근 거래, 외부 입력 파싱, 거래 분석성 API
- `client.budgets`: 예산, 장기 예산 목표, 월별 자본 목표
- `client.reports`: 통합 보고서, 요약 보고서, 사용자 정의 보고서 행
- `client.extras`: 자주입력, 매월입력, 카드 보고서, 캘린더, 포스트잇, 쪽지, 게시판, 업로드, 알림

## 설계 메모

- 런타임 HTTP 처리는 `httpx`를 사용합니다.
- API 모델은 가능한 범위에서 타입이 없는 딕셔너리 대신 명시적인 타입 구조로 정의합니다.
- 인증은 API key, Bearer token, OAuth 2.0 PKCE, OAuth 1.0a 헤더 생성을 지원합니다.
- API 응답에는 요청 가능 횟수 정보가 포함되므로, 클라이언트 표면에서도 해당 메타데이터를
  버리지 않고 보존합니다.
- 동기/비동기 클라이언트가 같은 리소스 경로 생성 로직을 공유하도록 구성합니다.
