# CLI 설계 메모

이 문서는 `whooing-py` 위에 CLI를 같은 저장소에서 확장할 때의 경계를 정의합니다.

## 기본 방향

- 라이브러리 패키지(`whooing`)는 HTTP 호출, 인증 헤더 생성, OAuth 토큰 교환, 응답 파싱,
  예외 매핑만 담당합니다.
- CLI는 사용자 입력, 프로필 선택, 토큰 저장, 출력 포맷, 종료 코드 정책을 담당합니다.
- CLI 때문에 라이브러리 API가 암묵적인 전역 설정이나 로컬 파일 상태를 갖지 않도록 합니다.

## 설치 경계

초기 CLI는 추가 런타임 의존성 없이 `argparse` 기반으로 유지합니다. `typer`, `rich` 같은
의존성은 명령 수가 늘고 출력 포맷 요구가 명확해진 뒤 optional extra로 도입합니다.

이 접근의 장점:

- 기본 라이브러리 설치가 가볍습니다.
- CLI가 있어도 라이브러리 사용자는 추가 의존성을 강제받지 않습니다.
- 초기 명령은 표준 라이브러리만으로 테스트하기 쉽습니다.

기회비용:

- 복잡한 중첩 명령, 자동 완성, 테이블 출력은 직접 구현해야 합니다.
- 명령이 늘어나면 `argparse` 코드가 장황해질 수 있습니다.

## 인증과 토큰 저장

라이브러리는 토큰 저장소를 제공하지 않습니다. CLI에서 필요한 저장 정책을 별도로 결정합니다.

권장 우선순위:

1. 환경 변수: `WHOOING_API_KEY`, `WHOOING_ACCESS_TOKEN`
2. 명시적 옵션: `--api-key`, `--access-token`
3. CLI 프로필 파일: 운영체제별 사용자 설정 디렉터리
4. OS keychain: 필요해질 때 별도 optional dependency로 도입

토큰 저장소가 추가되더라도 라이브러리 클라이언트는 `api_key`, `access_token`, `auth`를
명시적으로 받는 현재 형태를 유지합니다.

## 출력 정책

명령 출력은 처음부터 기계가 읽을 수 있는 JSON을 기본값으로 둡니다. 테이블이나 CSV 출력은
실제 사용 패턴이 확인된 뒤 추가합니다.

권장 출력 모드:

- `json`: 기본값, 원본 API 응답 보존
- `table`: 사람이 읽기 쉬운 목록 출력
- `csv`: 거래나 보고서 export용

## 예외 처리

CLI는 라이브러리 예외를 잡아 종료 코드와 메시지로 변환합니다.

- `WhooingAuthError`: 인증 실패
- `WhooingRateLimitError`: API 제한, `retry_after`가 있으면 재시도 안내에 사용
- `WhooingResponseError`: HTTP 또는 JSON 응답 오류
- `WhooingTransportError`: 네트워크 전송 오류

라이브러리 예외에는 CLI가 판단할 수 있는 구조화된 속성을 우선 추가하고, 문자열 메시지
파싱에 의존하지 않습니다.

## 초기 명령 범위

초기 CLI는 네트워크 호출이 필요 없는 명령부터 시작합니다.

```sh
whooing auth oauth2-url --client-id app --redirect-uri http://localhost/callback --scope read
```

이후 네트워크 호출 명령은 인증 입력, 출력 포맷, 오류 종료 코드 정책이 정리된 뒤 추가합니다.
