# whooing-py

[후잉 개발자 API](https://whooing.com/api/docs)를 위한 Python 클라이언트 라이브러리입니다.

## 상태

현재 이 저장소는 프로젝트 기반만 구성한 상태입니다. 공식 문서의 API 표면을 정리한 뒤 공개
클라이언트 API, 요청 모델, 응답 모델, 인증 헬퍼, 에러 처리를 추가할 예정입니다.

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

## 설계 메모

- 런타임 HTTP 처리는 `httpx`를 사용합니다.
- API 모델은 가능한 범위에서 타입이 없는 딕셔너리 대신 명시적인 타입 구조로 정의합니다.
- 인증은 API key와 OAuth 2.0 PKCE를 먼저 지원합니다. OAuth 1.0a는 필요할 경우 호환성
  레이어로 다룹니다.
- API 응답에는 요청 가능 횟수 정보가 포함되므로, 클라이언트 표면에서도 해당 메타데이터를
  버리지 않고 보존합니다.
