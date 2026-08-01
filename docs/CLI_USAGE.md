# CLI 사용 가이드

이 문서는 사람과 AI 에이전트가 `whooing` CLI만 보고 후잉 정보를 안전하게 조회할 수 있도록
목적별 명령을 정리합니다. 정보 조회가 목적이면 먼저 읽기 전용 명령을 사용하고, 생성/수정/삭제
명령은 사용자가 명시적으로 요청한 경우에만 실행합니다.

## 설치

`uv tool`로 설치하면 프로젝트 가상환경이나 `asdf`의 Python 버전과 독립적으로 관리되며,
현재 사용자는 어느 디렉터리에서나 `whooing` 명령을 실행할 수 있습니다.

```sh
uv tool install whooing-py
whooing --help
```

명령을 찾지 못하면 한 번만 실행 경로를 셸에 등록한 뒤 터미널을 다시 시작합니다. 실제 실행
파일 디렉터리는 `uv tool dir --bin`으로 확인할 수 있습니다.

```sh
uv tool update-shell
uv tool dir --bin
```

설치하지 않고 일회성으로 실행할 수도 있습니다.

```sh
uvx --from whooing-py whooing --help
```

## AI 에이전트 실행 규약

AI 에이전트는 다음 순서로 명령을 선택합니다.

1. `whooing --help`와 `whooing GROUP --help`로 전용 명령을 찾습니다.
2. 인증 상태와 대상 섹션이 불명확하면 `auth status`, `sections list`처럼 데이터를 바꾸지 않는
   명령으로 확인합니다.
3. 전용 `[READ]` 명령을 우선 사용하고 자동화에서는 기본값인 JSON 출력을 유지합니다.
4. `[WRITE]` 명령은 사용자가 해당 변경을 명시적으로 요청한 경우에만 사용합니다. 실행 전에
   조회 명령으로 대상 ID와 현재 상태를 확인합니다.
5. 전용 명령이 없는 API 경로만 `api request`로 호출합니다. `GET` 이외의 메서드는 변경
   작업으로 취급합니다.
6. 종료 코드가 0일 때만 성공으로 판단합니다. 실패한 생성·전송 명령은 현재 상태를 조회하기
   전까지 자동으로 재실행하지 않습니다.

도움말 설명의 태그는 다음 의미입니다.

| 태그 | 의미 | 실행 조건 |
| --- | --- | --- |
| `[READ]` | 원격 데이터를 조회하며 회계 데이터를 변경하지 않음 | 요청 해결에 필요하면 실행 가능 |
| `[WRITE]` | 원격 데이터·상태를 생성, 수정, 삭제 또는 전송함 | 사용자의 명시적 변경 요청 필요 |
| `[LOCAL READ]` | 로컬 프로필의 비밀이 아닌 메타데이터를 조회함 | 필요하면 실행 가능 |
| `[LOCAL WRITE]` | 로컬 프로필이나 인증 정보를 저장·삭제함 | 사용자의 로그인·설정 요청 필요 |
| `[AUTH]` | 저수준 인증 플로우이며 출력에 토큰이 포함될 수 있음 | 결과를 외부에 노출하지 않음 |
| `[DYNAMIC]` | HTTP 메서드에 따라 읽기/쓰기가 달라지는 범용 호출 | `GET`만 기본적으로 읽기로 취급 |

명령의 옵션과 인자까지 확인하려면 가장 구체적인 단계에서 `--help`를 실행합니다.

```sh
whooing --help
whooing entries --help
whooing entries list --help
```

## 기본 규칙

- 기본 출력은 JSON입니다. 자동화나 AI 에이전트는 JSON 출력을 우선 사용합니다.
- `table`과 `csv`는 API envelope 메타데이터를 생략하고 `results`를 평탄화할 수 있습니다.
  사람이 확인하거나 내보낼 때만 사용합니다.
- 전역 옵션은 하위 명령 앞에 둡니다.
- 현재 디렉터리에 `.env`가 있으면 CLI가 자동으로 읽습니다.
- 셸에 export된 `WHOOING_API_KEY` 또는 `WHOOING_ACCESS_TOKEN`이 있으면 `.env`보다 우선합니다.
- 프로필 저장은 명시적 작업입니다. 환경 변수 값을 프로필에 저장하려면 `profile set --from-env`를
  사용합니다.
- 프로필에는 API key와 access token 중 하나만 저장됩니다. 다른 인증 방식으로 다시 저장하면
  기존 값은 제거되며, 프로필 파일은 소유자만 읽고 쓸 수 있도록 저장됩니다.
- `auth login`은 후잉 AI 연동 키를 숨김 입력으로 받아 검증하고 기본 섹션과 함께 현재
  프로필에 저장합니다.
- 섹션 ID는 명령의 `--section-id`, `WHOOING_SECTION_ID`, 현재 프로필 순서로 결정됩니다.
- API key, access token, 프로필 파일 또는 `.env`를 로그·프롬프트·외부 메시지에 포함하지
  않습니다. `auth exchange-code`, `auth refresh`, OAuth 1.0a 저수준 명령의 출력도 비밀로
  취급합니다.

```sh
whooing --output json sections list
whooing --output table sections list
whooing --profile default sections list
whooing --api-key "$WHOOING_API_KEY" sections list
whooing profile set --from-env
```

## 인증과 설정 해석 순서

인증 정보는 다음 우선순위에서 처음 발견한 한 가지 방식만 사용합니다.

1. 전역 옵션 `--api-key` 또는 `--access-token`
2. 환경 변수 `WHOOING_API_KEY` 또는 `WHOOING_ACCESS_TOKEN`
3. `--profile`로 선택한 로컬 프로필

API key와 access token을 같은 우선순위에 동시에 제공하면 오류가 발생합니다. 현재 작업
디렉터리의 `.env`는 프로세스 환경에 없는 값만 채우므로 셸 환경 변수가 우선합니다.

섹션 ID는 다음 순서로 결정됩니다.

1. 하위 명령의 `--section-id`
2. 환경 변수 `WHOOING_SECTION_ID`
3. 선택한 로컬 프로필의 기본 섹션

`api request`에는 섹션 ID가 자동으로 추가되지 않습니다. 필요한 경우 `--param
section_id=SECTION_ID` 또는 쓰기 요청의 `--data section_id=SECTION_ID`로 명시합니다.

## 최초 로그인

개인용 CLI는 별도 App 등록이 필요하지 않습니다. 로그인 명령을 실행한 뒤 안내에 따라 후잉
`계정 > 비밀번호 및 보안 > +AI 연동`에서 키를 발급하고 숨김 프롬프트에 붙여 넣습니다.

```sh
whooing auth login

# 브라우저를 자동으로 열 수 없는 환경
whooing auth login --no-browser
```

CLI는 키로 기본 섹션을 조회하여 인증을 검증한 뒤 키와 section ID를 현재 프로필에 저장합니다.
키는 프롬프트와 최종 출력에 표시되지 않습니다.

상태 확인과 로그아웃:

```sh
whooing auth status
whooing auth logout
```

AI 연동 키 프로필에서 `auth logout`은 로컬 프로필만 제거합니다. 키 자체를 폐기하려면 후잉
`비밀번호 및 보안` 화면에서 AI 연동을 해제해야 합니다.

배포용 App ID를 이미 보유한 개발자는 OAuth 2.0 PKCE 로그인을 사용할 수 있습니다. 기본
scope는 읽기 전용 `read`입니다.

```sh
whooing auth oauth-login --client-id APP_ID
whooing --profile writer auth oauth-login \
  --client-id APP_ID \
  --scope read \
  --scope write
```

## 인증 확인

먼저 사용자 정보나 섹션 목록 조회로 인증을 확인합니다.

```sh
whooing user get
whooing sections list
```

대화형 로그인을 사용하지 않는 자동화 환경에서는 다음 환경 변수 방식을 사용할 수 있습니다.

```sh
export WHOOING_API_KEY=...
export WHOOING_ACCESS_TOKEN=...
```

또는 현재 디렉터리에 `.env`를 둡니다.

```dotenv
WHOOING_API_KEY=...
WHOOING_SECTION_ID=...
```

## 섹션 ID 찾기

대부분의 재무 데이터 조회에는 `section_id`가 필요합니다. 사용자가 섹션 ID를 주지 않았다면
OAuth 로그인에서 저장된 기본 섹션을 우선 사용합니다. 기본 섹션을 변경하거나 API key
프로필에 처음 저장하려면 다음 명령을 사용합니다.

```sh
whooing sections list
whooing profile set --section-id s123
```

이후에는 `--section-id`를 생략할 수 있습니다.

```sh
whooing accounts list
whooing entries latest
```

저장된 기본값을 한 명령에서만 덮어쓸 수도 있습니다.

```sh
whooing accounts list --section-id s456
```

## 도메인 값과 식별자

문서의 대문자 표기는 실제 값으로 치환하는 자리표시자이며 그대로 전달하지 않습니다.

| 자리표시자 | 의미 | 확인 명령 |
| --- | --- | --- |
| `SECTION_ID` | 후잉 장부(섹션) 식별자 | `whooing sections list` |
| `ACCOUNT_ID` | 자산·부채·자본·수입·비용 항목 식별자 | `whooing accounts list` |
| `ENTRY_ID` | 거래 식별자 | `whooing entries list` 또는 `entries latest` |
| `CUSTOM_ID` | 사용자 정의 보고서 행 식별자 | `whooing reports custom-rows` |

계정 그룹은 `assets`, `liabilities`, `capital`, `income`, `expenses` 중 하나입니다. 표시 이름이
아닌 API 식별자를 인자에 전달합니다. 거래 날짜는 일반적으로 `YYYYMMDD`, 월은 `YYYYMM`
형식으로 전달하며 API별 요구 형식은 해당 명령의 예와 후잉 API 문서를 확인합니다.

사용자가 이름만 제공했을 때 ID를 임의 생성하거나 추측하지 않습니다. 조회 결과에서 정확히
하나로 식별되지 않으면 후보를 제시하고 사용자의 선택을 받습니다.

## 읽기 전용 목적별 명령

### 자연어 요청 매핑

AI 에이전트는 사용자의 요청을 다음 명령으로 우선 매핑합니다.

| 사용자가 원하는 정보 | 우선 실행할 명령 |
| --- | --- |
| 내 후잉 사용자 정보 | `whooing user get` |
| 장부 또는 섹션 목록 | `whooing sections list` |
| 기본 섹션 | `whooing sections default` |
| 계정 목록, 자산/부채/수입/지출 항목 | `whooing accounts list` |
| 특정 계정 그룹 | `whooing accounts list --account assets` |
| 최근 거래 | `whooing entries latest` |
| 특정 기간 거래 | `whooing entries list --param start_date=YYYYMMDD --param end_date=YYYYMMDD` |
| 최근 사용한 거래 항목 | `whooing entries latest-items` |
| 예산 | `whooing budgets get expenses` |
| 장기 예산 목표 | `whooing budgets goal` |
| 자산 목표 | `whooing budgets capital-goal` |
| 재무 보고서, 잔액 보고서 | `whooing reports report` |
| 수입/지출 요약 | `whooing reports summary --account expenses` |
| 카드 사용 내역 | `whooing extras bill` 또는 `whooing extras checkcard` |
| 입출금 흐름 | `whooing extras in-out` |
| 달력 보기 | `whooing extras calendar` |
| 알림 | `whooing extras notifications` |

### 내 정보

```sh
whooing user get
whooing user logs
whooing user point-logs
```

### 섹션

```sh
whooing sections list
whooing sections get SECTION_ID
whooing sections default
```

### 계정과 잔액

전체 계정 목록:

```sh
whooing accounts list --section-id SECTION_ID
```

특정 계정 그룹만 조회:

```sh
whooing accounts list --section-id SECTION_ID --account assets
whooing accounts list --section-id SECTION_ID --account liabilities
whooing accounts list --section-id SECTION_ID --account capital
whooing accounts list --section-id SECTION_ID --account expenses
whooing accounts list --section-id SECTION_ID --account income
```

특정 계정 상세:

```sh
whooing accounts get assets ACCOUNT_ID --section-id SECTION_ID
whooing accounts exists assets ACCOUNT_ID --section-id SECTION_ID
```

### 거래

최근 거래:

```sh
whooing entries latest --section-id SECTION_ID
```

거래 목록:

```sh
whooing entries list --section-id SECTION_ID --param start_date=20260101 --param end_date=20260131
```

특정 거래:

```sh
whooing entries get ENTRY_ID --section-id SECTION_ID
```

최근 사용 항목:

```sh
whooing entries latest-items --section-id SECTION_ID
```

거래 분석:

```sh
whooing entries analytics flow_of_account --section-id SECTION_ID
whooing entries analytics changes_of_item --section-id SECTION_ID --param start_date=20260101
```

### 예산

```sh
whooing budgets get expenses --section-id SECTION_ID
whooing budgets goal --section-id SECTION_ID
whooing budgets capital-goal --section-id SECTION_ID
```

### 보고서

통합 보고서:

```sh
whooing reports report --section-id SECTION_ID
whooing reports report --account assets --section-id SECTION_ID
whooing reports report --account assets --account-id ACCOUNT_ID --section-id SECTION_ID
```

요약 보고서:

```sh
whooing reports summary --section-id SECTION_ID
whooing reports summary --account expenses --section-id SECTION_ID
```

사용자 정의 보고서 행:

```sh
whooing reports custom-rows --section-id SECTION_ID --report report_bs
whooing reports custom-rows --section-id SECTION_ID --report report_pl --action info --custom-id CUSTOM_ID
```

### 부가 기능

카드, 입출금, 캘린더:

```sh
whooing extras bill --section-id SECTION_ID
whooing extras checkcard --section-id SECTION_ID
whooing extras in-out --section-id SECTION_ID
whooing extras calendar --section-id SECTION_ID
```

반복 입력 항목:

```sh
whooing extras frequent-items --section-id SECTION_ID
whooing extras frequent-items --slot slot1 --section-id SECTION_ID
whooing extras monthly-items --section-id SECTION_ID
whooing extras monthly-items --slot slot1 --section-id SECTION_ID
```

포스트잇, 쪽지, 게시판, 알림:

```sh
whooing extras post-its --section-id SECTION_ID
whooing extras messages
whooing extras unread-messages
whooing extras bbs
whooing extras notifications --section-id SECTION_ID
```

## 파라미터와 출력

`--param`, `--data`, `--field`는 `key=value` 형식입니다. 값은 JSON scalar로 해석 가능한 경우
숫자, boolean, null로 변환됩니다. JSON scalar로만 구성된 배열도 배열로 전달하며, 그 외 값은
문자열로 전달합니다. 같은 key를 반복하면 마지막 값이 앞의 값을 덮어씁니다.

```sh
whooing entries list --section-id SECTION_ID --param limit=20
whooing entries list --section-id SECTION_ID --param memo=커피
whooing entries list --section-id SECTION_ID --param include_disabled=false
```

출력 형식:

```sh
whooing --output json entries latest --section-id SECTION_ID
whooing --output table accounts list --section-id SECTION_ID
whooing --output csv entries latest --section-id SECTION_ID
```

### JSON 출력 계약

성공한 API 명령은 후잉 API의 전체 JSON envelope을 표준 출력(stdout)에 기록합니다. 일반적으로
다음 필드를 포함합니다.

```json
{
  "code": 200,
  "results": [],
  "rest_of_api": 999
}
```

- `code`: 후잉 API 결과 코드
- `results`: 명령별 실제 결과 객체 또는 배열
- `rest_of_api`: 남은 API 호출 가능 횟수
- 그 밖의 필드: 후잉 원본 응답에 포함된 메타데이터

필드의 존재나 `results`의 객체·배열 형태를 명령 간에 추측하지 않고 실제 JSON을 검사합니다.
전용 명령은 출력 전에 명령별 Pydantic 모델로 응답 구조를 검증합니다.

### 오류와 종료 코드

| 종료 코드 | 의미 | 출력 위치 |
| --- | --- | --- |
| `0` | 명령 성공 | 결과는 stdout |
| `1` | 인증, 설정, 네트워크, API 응답 또는 응답 검증 실패 | 오류는 stderr |
| `2` | 알 수 없는 옵션, 필수 인자 누락 등 CLI 사용 오류 | 사용법과 오류는 stderr |

Whooing 라이브러리 오류는 `error`, `message`와 오류 유형별 메타데이터를 가진 JSON으로 stderr에
출력됩니다. CLI 인자와 로컬 설정 오류는 일반 텍스트일 수 있으므로 실패 출력이 항상 JSON이라고
가정하지 않습니다. stdout의 JSON 존재 여부만으로 성공을 판단하지 말고 종료 코드를 먼저
확인합니다.

## 직접 API 호출

전용 명령을 찾기 어렵거나 새 엔드포인트를 호출해야 할 때는 `api request`를 사용합니다.

```sh
whooing api request GET sections.json
whooing api request GET entries/latest.json --param section_id=SECTION_ID
whooing api request POST entries/outside_report.json --data source=...
```

`api request`는 공통 후잉 응답 envelope만 검증합니다. 전용 명령은 리소스별 Pydantic 응답
모델까지 검증합니다. `api request`를 사용할 때 경로와 파라미터를 추측하지 않고 후잉 API
문서에서 확인합니다.

## 변경 명령 주의

다음 명령은 실제 데이터를 변경합니다. 사용자가 명시적으로 생성, 수정, 삭제를 요청한 경우에만
실행합니다.

- `sections create`, `sections update`, `sections delete`, `sections sort`
- `accounts create`, `accounts update`, `accounts delete`, `accounts sort`
- `entries create`, `entries update`, `entries update-many`, `entries delete`
- `entries report-outside-source`
- `budgets update`, `budgets update-basic-total`, `budgets delete`, `budgets update-goal`,
  `budgets delete-goal`, `budgets update-capital-goal`
- `reports update-custom-rows`
- `extras create-*`, `extras update-*`, `extras delete-*`, `extras sort-*`,
  `extras send-message`, `extras recommend-bbs`, `extras prepare-upload`,
  `extras complete-upload`, `extras mark-notifications-read`

변경 명령을 사용해야 한다면 먼저 대응되는 조회 명령으로 `section_id`, `account_id`, `entry_id`
같은 식별자와 현재 값을 확인합니다. 삭제·일괄 수정·정렬은 전달한 모든 ID와 순서를 실행 직전에
다시 검증합니다.

생성, 메시지 전송, 업로드 완료처럼 중복 실행의 영향이 큰 명령이 네트워크 오류나 타임아웃으로
끝나면 서버 반영 여부가 불명확할 수 있습니다. 같은 명령을 즉시 반복하지 말고 대응되는 조회
명령으로 결과를 확인한 뒤 필요한 경우에만 재실행합니다.
