# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

공개 API가 안정화되는 동안에도 버전은 semantic versioning을 기준으로 관리합니다.

## 0.2.1 - 2026-08-08

- 런타임 및 개발 의존성을 최신 호환 버전으로 갱신했습니다.
- GitHub Actions 의존성과 `cryptography` 보안 업데이트를 반영했습니다.

## 0.2.0 - 2026-08-01

- 후잉의 개인용 외부 도구 정책에 맞춰 `whooing auth login`이 AI 연동 키를 숨김 입력으로
  받아 검증·저장하도록 변경하고, 배포용 앱 OAuth 로그인은 `auth oauth-login`으로
  분리했습니다.
- OAuth 2.0 PKCE 브라우저 승인, localhost callback, token 교환과 프로필 저장을 한 번에
  수행하는 `whooing auth oauth-login`을 추가했습니다.
- OAuth 로그인 프로필에 refresh token, App ID, scope와 기본 section ID를 저장하고
  `auth status`, `auth logout` 명령을 추가했습니다.
- 리소스 명령이 명시 옵션, 환경 변수, 프로필 순서로 기본 section ID를 해석하도록
  개선했습니다.
- 보고서와 부가 기능 명령에 전용 `--section-id` 옵션을 추가했습니다.
- AI 에이전트가 안전하게 명령을 선택할 수 있도록 모든 CLI 명령에 읽기·쓰기 태그와 구체적인
  도움말을 추가하고, 인증 우선순위·출력 계약·종료 코드를 문서화했습니다.

## 0.1.0 - 2026-07-29

- 타입 힌트를 제공하는 후잉 개발자 API 클라이언트 초기 구현을 추가했습니다.
- 동기/비동기 클라이언트를 추가했습니다.
- API key, Bearer token, OAuth 1.0a, OAuth 2.0 PKCE, Onetime PIN 인증 헬퍼를
  추가했습니다.
- Pydantic 응답 모델과 CLI 요청/응답 검증을 추가했습니다.
- 자주 사용하는 쓰기 API용 요청 모델을 추가했습니다.
- Typer 기반 CLI를 추가해 인증, 프로필, 범용 API 요청, 주요 리소스 조회와 변경 명령을
  지원합니다.
- CLI에서 글로벌 환경 변수와 현재 디렉터리 `.env`를 읽도록 하고, 환경 변수 기반 프로필
  저장은 `profile set --from-env`로 명시화했습니다.
- AI와 자동화 도구가 목적별 CLI 명령을 고를 수 있도록 `docs/CLI_USAGE.md`를 추가했습니다.
- GitHub Actions와 pre-commit 기반 로컬 검증 구성을 추가했습니다.
- 재현 가능한 CI를 위해 `uv.lock`을 추적하고 실제 API 통합 테스트를 분리했습니다.
- PyPI Trusted Publishing 기반의 태그 검증 및 배포 자동화를 추가했습니다.
- 사용자, 섹션, 계정, 거래, 장기 목표, 반복 거래, 포스트잇, 메시지, 게시판 요청
  모델의 필드명을 현재 후잉 개발자 API 문서와 일치시켰습니다.
- 성공 및 OAuth 응답이 JSON 객체가 아닐 때 패키지 응답 예외로 정규화합니다.
- 중복 생성을 방지하기 위해 POST 요청은 기본 자동 재시도 대상에서 제외합니다.
- OAuth2 token 폐기의 빈 성공 응답과 OAuth1 request-token의 callback redirect 응답을
  지원합니다.
- 빈 명시 옵션이나 환경 변수를 인증 정보로 사용하지 않도록 인증 입력 경계를 강화했습니다.
- 일괄 거래 건수와 장기 예산 월별 배분의 공식 요청 제한을 호출 전에 검증합니다.
