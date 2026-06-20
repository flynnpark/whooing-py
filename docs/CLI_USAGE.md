# CLI 사용 가이드

이 문서는 사람과 AI 에이전트가 `whooing` CLI만 보고 후잉 정보를 안전하게 조회할 수 있도록
목적별 명령을 정리합니다. 정보 조회가 목적이면 먼저 읽기 전용 명령을 사용하고, 생성/수정/삭제
명령은 사용자가 명시적으로 요청한 경우에만 실행합니다.

## 기본 규칙

- 기본 출력은 JSON입니다. 자동화나 AI 에이전트는 JSON 출력을 우선 사용합니다.
- 사람이 표로 확인할 때만 `--output table`을 사용합니다.
- 전역 옵션은 하위 명령 앞에 둡니다.
- 현재 디렉터리에 `.env`가 있으면 CLI가 자동으로 읽습니다.
- 셸에 export된 `WHOOING_API_KEY` 또는 `WHOOING_ACCESS_TOKEN`이 있으면 `.env`보다 우선합니다.
- 프로필 저장은 명시적 작업입니다. 환경 변수 값을 프로필에 저장하려면 `profile set --from-env`를
  사용합니다.

```sh
whooing --output json sections list
whooing --output table sections list
whooing --profile default sections list
whooing --api-key "$WHOOING_API_KEY" sections list
whooing profile set --from-env
```

## 인증 확인

먼저 사용자 정보나 섹션 목록 조회로 인증을 확인합니다.

```sh
whooing user get
whooing sections list
```

인증이 없으면 다음 중 하나를 설정합니다.

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
먼저 섹션 목록을 조회합니다.

```sh
whooing sections list
```

응답의 `results[].section_id` 중 사용할 값을 골라 이후 명령에 넘깁니다.

```sh
whooing accounts list --section-id "$WHOOING_SECTION_ID"
whooing entries latest --section-id "$WHOOING_SECTION_ID"
```

## 읽기 전용 목적별 명령

### 자연어 요청 매핑

AI 에이전트는 사용자의 요청을 다음 명령으로 우선 매핑합니다.

| 사용자가 원하는 정보 | 우선 실행할 명령 |
| --- | --- |
| 내 후잉 사용자 정보 | `whooing user get` |
| 장부 또는 섹션 목록 | `whooing sections list` |
| 기본 섹션 | `whooing sections default` |
| 계정 목록, 자산/부채/수입/지출 항목 | `whooing accounts list --section-id SECTION_ID` |
| 특정 계정 그룹 | `whooing accounts list --section-id SECTION_ID --account assets` |
| 최근 거래 | `whooing entries latest --section-id SECTION_ID` |
| 특정 기간 거래 | `whooing entries list --section-id SECTION_ID --param start_date=YYYYMMDD --param end_date=YYYYMMDD` |
| 최근 사용한 거래 항목 | `whooing entries latest-items --section-id SECTION_ID` |
| 예산 | `whooing budgets get expenses --section-id SECTION_ID` |
| 장기 예산 목표 | `whooing budgets goal --section-id SECTION_ID` |
| 자산 목표 | `whooing budgets capital-goal --section-id SECTION_ID` |
| 재무 보고서, 잔액 보고서 | `whooing reports report --param section_id=SECTION_ID` |
| 수입/지출 요약 | `whooing reports summary --account expenses --param section_id=SECTION_ID` |
| 카드 사용 내역 | `whooing extras bill --param section_id=SECTION_ID` 또는 `whooing extras checkcard --param section_id=SECTION_ID` |
| 입출금 흐름 | `whooing extras in-out --param section_id=SECTION_ID` |
| 달력 보기 | `whooing extras calendar --param section_id=SECTION_ID` |
| 알림 | `whooing extras notifications --section-id SECTION_ID` |

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
whooing reports report --param section_id=SECTION_ID
whooing reports report --account assets --param section_id=SECTION_ID
whooing reports report --account assets --account-id ACCOUNT_ID --param section_id=SECTION_ID
```

요약 보고서:

```sh
whooing reports summary --param section_id=SECTION_ID
whooing reports summary --account expenses --param section_id=SECTION_ID
```

사용자 정의 보고서 행:

```sh
whooing reports custom-rows --section-id SECTION_ID --report report_bs
whooing reports custom-rows --section-id SECTION_ID --report report_pl --action info --custom-id CUSTOM_ID
```

### 부가 기능

카드, 입출금, 캘린더:

```sh
whooing extras bill --param section_id=SECTION_ID
whooing extras checkcard --param section_id=SECTION_ID
whooing extras in-out --param section_id=SECTION_ID
whooing extras calendar --param section_id=SECTION_ID
```

반복 입력 항목:

```sh
whooing extras frequent-items --param section_id=SECTION_ID
whooing extras frequent-items --slot slot1 --param section_id=SECTION_ID
whooing extras monthly-items --param section_id=SECTION_ID
whooing extras monthly-items --slot slot1 --param section_id=SECTION_ID
```

포스트잇, 쪽지, 게시판, 알림:

```sh
whooing extras post-its --param section_id=SECTION_ID
whooing extras messages
whooing extras unread-messages
whooing extras bbs
whooing extras notifications --section-id SECTION_ID
```

## 파라미터와 출력

`--param`, `--data`, `--field`는 `key=value` 형식입니다. 값은 JSON scalar로 해석 가능한 경우
숫자, boolean, null로 변환됩니다. 그 외 값은 문자열로 전달합니다.

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

## 직접 API 호출

전용 명령을 찾기 어렵거나 새 엔드포인트를 호출해야 할 때는 `api request`를 사용합니다.

```sh
whooing api request GET sections.json
whooing api request GET entries/latest.json --param section_id=SECTION_ID
whooing api request POST entries/outside_report.json --data source=...
```

`api request`는 공통 후잉 응답 envelope만 검증합니다. 전용 명령은 리소스별 Pydantic 응답
모델까지 검증합니다.

## 변경 명령 주의

다음 명령은 실제 데이터를 변경합니다. 사용자가 명시적으로 생성, 수정, 삭제를 요청한 경우에만
실행합니다.

- `sections create`, `sections update`, `sections delete`, `sections sort`
- `accounts create`, `accounts update`, `accounts delete`, `accounts sort`
- `entries create`, `entries update`, `entries update-many`, `entries delete`
- `budgets update`, `budgets update-basic-total`, `budgets delete`, `budgets update-goal`,
  `budgets delete-goal`, `budgets update-capital-goal`
- `reports update-custom-rows`
- `extras create-*`, `extras update-*`, `extras delete-*`, `extras sort-*`,
  `extras send-message`, `extras recommend-bbs`, `extras prepare-upload`,
  `extras complete-upload`, `extras mark-notifications-read`

변경 명령을 사용해야 한다면 먼저 대응되는 조회 명령으로 `section_id`, `account_id`, `entry_id`
같은 식별자를 확인합니다.
