# 릴리스 체크리스트

새 패키지 버전을 배포하기 전에 이 체크리스트를 따릅니다.

## 최초 설정

PyPI에서 `whooing-py` pending Trusted Publisher를 다음 값으로 등록합니다.

- PyPI project name: `whooing-py`
- GitHub owner: `flynnpark`
- GitHub repository: `whooing-py`
- Workflow: `release.yml`
- Environment: `pypi`

GitHub 저장소에는 `pypi` environment를 만들고, 필요하면 배포 승인 규칙을 설정합니다.
릴리스 workflow는 장기 API token 없이 GitHub OIDC로 PyPI의 단기 배포 토큰을 발급받습니다.

## 사전 확인

- `README.md` 예제가 공개 API와 일치하는지 확인합니다.
- 새로 추가하거나 제거한 엔드포인트 래퍼가 `docs/API_COVERAGE.md`에 반영됐는지
  확인합니다.
- 사용자가 인지할 수 있는 변경 사항을 `CHANGELOG.md`에 추가합니다.
- `CHANGELOG.md`의 대상 버전에서 `Unreleased`를 실제 배포 날짜로 변경합니다.
- `pyproject.toml`의 `version`과 `src/whooing/__init__.py`의 `__version__`을 함께
  갱신합니다.

## 검증

```sh
uv sync --locked --dev
uv lock --check
uv run --locked pre-commit run --all-files
uv run --locked ruff check .
uv run --locked mypy src
uv run --locked pytest
uv build
```

유효한 후잉 인증 정보가 있을 때만 통합 테스트를 실행합니다.

```sh
WHOOING_API_KEY=... WHOOING_SECTION_ID=... uv run --locked pytest -m integration
```

## 배포

- 버전과 일치하는 서명된 `v<version>` 태그를 만들고 push합니다.
- 해당 태그로 GitHub Release를 발행합니다.
- `Publish to PyPI` workflow의 build와 publish job이 모두 성공했는지 확인합니다.
- PyPI 페이지에서 README와 패키지 메타데이터가 정상적으로 렌더링되는지 확인합니다.

예를 들어 0.1.0을 배포할 때는 다음 순서로 진행합니다.

```sh
git tag -s v0.1.0 -m "whooing-py 0.1.0"
git push origin v0.1.0
gh release create v0.1.0 --verify-tag --title "whooing-py 0.1.0" --notes-from-tag
```

GitHub Release의 `published` 이벤트가 발생하면 `.github/workflows/release.yml`이 태그와
패키지 버전의 일치 여부를 확인하고, wheel과 sdist를 빌드·검증한 뒤 PyPI에 게시합니다.
