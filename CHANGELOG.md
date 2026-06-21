# Changelog

이 프로젝트의 주요 변경 사항을 기록합니다.

공개 API가 안정화되는 동안에도 버전은 semantic versioning을 기준으로 관리합니다.

## 0.1.0 - 2026-06-21

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
