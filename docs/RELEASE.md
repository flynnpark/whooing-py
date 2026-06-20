# 릴리스 체크리스트

새 패키지 버전을 배포하기 전에 이 체크리스트를 따릅니다.

## 사전 확인

- `README.md` 예제가 공개 API와 일치하는지 확인합니다.
- 새로 추가하거나 제거한 엔드포인트 래퍼가 `docs/API_COVERAGE.md`에 반영됐는지
  확인합니다.
- 사용자가 인지할 수 있는 변경 사항을 `CHANGELOG.md`에 추가합니다.
- `pyproject.toml`의 `version`과 `src/whooing/__init__.py`의 `__version__`을 함께
  갱신합니다.

## 검증

```sh
uv sync --extra pydantic --dev
uv run ruff check .
uv run mypy src
uv run pytest
uv build
```

유효한 후잉 인증 정보가 있을 때만 통합 테스트를 실행합니다.

```sh
WHOOING_API_KEY=... WHOOING_SECTION_ID=... uv run pytest -m integration
```

## 배포

- 서명된 릴리스 태그를 만들고 push합니다.
- `dist/`의 배포 파일을 PyPI에 업로드합니다.
- PyPI 페이지에서 README와 패키지 메타데이터가 정상적으로 렌더링되는지 확인합니다.
