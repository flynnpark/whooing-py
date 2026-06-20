# whooing-py

[후잉 개발자 API](https://whooing.com/api/docs)를 위한 Python 클라이언트 라이브러리입니다.

## 상태

공식 문서 기준의 1차 클라이언트 구현이 들어간 상태입니다. 동기/비동기 클라이언트, API
key/Bearer/OAuth 1.0a 인증 헤더, OAuth 1.0a 앱 인증 플로우, Onetime PIN, OAuth 2.0
PKCE 토큰 헬퍼, 주요 API 리소스 호출 메서드, 응답 메타데이터와 오류 매핑을 제공합니다.

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

Pydantic 응답 파싱 헬퍼까지 사용하려면 optional extra를 포함해 설치합니다.

```sh
uv sync --extra pydantic --dev
```

## 개발

```sh
uv run ruff check .
uv run mypy src
uv run pytest
uv build
```

실제 후잉 API 통합 테스트는 환경 변수가 있을 때만 실행됩니다.

```sh
WHOOING_API_KEY=... WHOOING_SECTION_ID=... uv run pytest -m integration
```

이 프로젝트에서만 자동으로 인식되게 하려면 `.env.example`을 참고해 `.env`를 만듭니다.
`.env`는 Git에서 무시됩니다.

```sh
WHOOING_API_KEY=발급된_인증키
WHOOING_SECTION_ID=s123
```

이후에는 별도 export 없이 실행할 수 있습니다.

```sh
uv run pytest -m integration
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

OAuth 1.0a 앱 인증:

```python
from whooing import AppAuthClient, OAuth1aAuth, WhooingClient

with AppAuthClient() as app_auth:
    request_token = app_auth.request_token(
        app_id="app_id",
        app_secret="app_secret",
        callback_uri="http://localhost/callback",
    )
    authorize_url = app_auth.build_authorization_url(token=request_token.token)
    access_token = app_auth.access_token(
        app_id="app_id",
        app_secret="app_secret",
        token=request_token.token,
        pin="pin",
    )

auth = OAuth1aAuth(
    app_id="app_id",
    app_secret="app_secret",
    token=access_token.token,
    token_secret=access_token.token_secret,
)

with WhooingClient(auth=auth) as client:
    user = client.users.get()
```

Onetime PIN 인증:

```python
from whooing import AppAuthClient

with AppAuthClient() as app_auth:
    access_token = app_auth.access_token_by_onetime(
        app_id="app_id",
        app_secret="app_secret",
        onetime_pin="pin",
    )
```

Pydantic 모델로 응답 파싱:

```python
from whooing import WhooingClient
from whooing.pydantic_models import Section


with WhooingClient(api_key="발급된_인증키") as client:
    response = client.sections.list()
    sections = response.parse_results_as(list[Section])
```

단일 객체 응답은 `response.parse_results(Model)`로, 전체 API 응답은
`response.parse(ResponseModel)`로 검증할 수 있습니다. 이 기능은 `pydantic` extra를
설치한 사용자에게만 제공되며, 기본 설치 사용자에게 Pydantic 의존성을 강제하지 않습니다.
공식 리소스별 모델은 `whooing.pydantic_models`에 모아 두었습니다.

공통 응답 규칙까지 엄밀하게 검증하려면 strict envelope 모델을 사용할 수 있습니다.

```python
from whooing import WhooingClient
from whooing.pydantic_models import User, WhooingSuccessResponse

with WhooingClient(api_key="발급된_인증키") as client:
    response = client.users.get()
    parsed = response.parse(WhooingSuccessResponse[User])
```

`whooing.pydantic_models`에는 일반 API의 성공/204/오류 응답, OAuth 오류, OAuth2 토큰,
OAuth2 metadata, OAuth1 토큰 응답 모델도 포함되어 있습니다.

요청 모델 사용:

```python
from whooing import EntryInput, WhooingClient

entry = EntryInput(
    entry_date=20260607,
    left_account="expenses",
    left_account_id="x1",
    right_account="assets",
    right_account_id="x2",
    item="커피",
    money=5000,
)

with WhooingClient(api_key="발급된_인증키") as client:
    client.entries.create_entry(section_id="s123", entry=entry)
```

파라미터가 많은 API는 `AccountInput`, `BudgetInput`, `PostItInput`, `MessageInput` 같은
dataclass 요청 모델을 제공합니다. 문서에 없는 필드나 새로 추가된 필드는 기존
`**fields` 방식 또는 요청 모델의 `extra_fields`로 전달할 수 있습니다.

선택적 재시도:

```python
from whooing import RetryPolicy, WhooingClient

with WhooingClient(
    api_key="발급된_인증키",
    retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=0.5),
) as client:
    response = client.users.get()
```

기본값은 재시도하지 않습니다. `RetryPolicy`를 명시한 경우에만 HTTP 429와 일시적인 5xx
응답을 제한된 횟수로 다시 시도합니다.

## 리소스 구성

- `client.users`: 사용자 정보, 사용자 로그, 포인트 로그
- `client.sections`: 섹션 조회/생성/수정/삭제/정렬
- `client.accounts`: 항목 조회/생성/수정/삭제/정렬
- `client.entries`: 거래 조회/입력/수정/삭제, 최근 거래, 외부 입력 파싱, 거래 분석성 API
- `client.budgets`: 예산, 장기 예산 목표, 월별 자본 목표
- `client.reports`: 통합 보고서, 요약 보고서, 사용자 정의 보고서 행
- `client.extras`: 자주입력, 매월입력, 카드 보고서, 캘린더, 포스트잇, 쪽지, 게시판, 업로드, 알림

## 커버리지

현재 구현은 공식 문서의 인증 플로우와 주요 API 경로를 호출할 수 있는 래퍼를 제공합니다.
다만 모든 응답 스키마를 Pydantic 모델로 고정하지는 않았습니다. 후잉 API 응답은 리소스별
형태가 넓기 때문에 기본값은 `ApiResponse[JsonValue]`이고, 필요한 사용자가 optional
Pydantic 헬퍼로 검증하는 방식을 택했습니다.

문서의 특정 엔드포인트 래퍼가 빠져 있더라도 `client.request(...)`와
`async_client.request(...)`로 직접 호출할 수 있습니다. 누락 래퍼는 테스트 가능한 단위로
추가하는 것을 기본 방향으로 합니다.

세부 구현 현황은 [API 구현 커버리지](docs/API_COVERAGE.md)를 기준으로 관리합니다.
릴리스 절차는 [릴리스 체크리스트](docs/RELEASE.md)를 따릅니다.

## 설계 메모

- 런타임 HTTP 처리는 `httpx`를 사용합니다.
- API 모델은 가능한 범위에서 타입이 없는 딕셔너리 대신 명시적인 타입 구조로 정의합니다.
- 인증은 API key, Bearer token, OAuth 2.0 PKCE, OAuth 1.0a 앱 인증, OAuth 1.0a 헤더
  생성을 지원합니다.
- API 응답에는 요청 가능 횟수 정보가 포함되므로, 클라이언트 표면에서도 해당 메타데이터를
  버리지 않고 보존합니다.
- 동기/비동기 클라이언트가 같은 리소스 경로 생성 로직을 공유하도록 구성합니다.
- 재시도는 기본 동작으로 강제하지 않고, `RetryPolicy`를 명시한 경우에만 적용합니다.
- Pydantic은 optional extra로만 제공해, 강한 응답 모델링을 원하는 사용자와 가벼운 기본
  설치를 원하는 사용자를 모두 지원합니다.
