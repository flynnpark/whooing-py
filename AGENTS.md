# Project Agent Instructions

## Commit Rules

- Before creating a commit, inspect recent history with `git log --oneline -n 20` and match the existing project convention.
- Commit messages must use the current convention:

  ```text
  type: Korean summary
  ```

- Allowed `type` values follow the repository history:
  - `feat`: user-visible capability or API addition
  - `fix`: bug fix or correctness fix
  - `refactor`: internal restructuring without behavior change
  - `test`: test-only changes or coverage expansion
  - `ci`: CI workflow changes
  - `docs`: documentation-only changes

- Use Korean for the summary. Keep it concise and specific.
- Do not use English imperative-only subjects such as `Add ...` or `Fix ...`.
- Stage only the files that belong to the intended commit. Do not mix unrelated working-tree changes.
- If a commit has already been made with a message that does not follow this convention, amend it before continuing when it is still local and safe to amend.

## Verification Rules

- This repository configures `pre-commit` with local hooks for `ruff check .` and `mypy src`.
- Do not rely on pre-commit alone before pushing; it does not run pytest or package builds.
- Before pushing, run the same checks as GitHub Actions when the change can affect code, tests, packaging, dependencies, or CLI behavior:

  ```sh
  uv sync --extra pydantic --dev
  uv run pre-commit run --all-files
  uv run ruff check .
  uv run mypy src
  uv run pytest
  uv build
  ```

- When a failure appears only in the CI matrix, reproduce the failing Python version locally with `uv run --python <version> ...` before changing code.
- Integration tests that depend on real Whooing credentials must remain skip-safe when credentials are missing, invalid, or unauthorized.

## CLI Documentation Rules

- When adding, renaming, or changing CLI commands or authentication behavior, update `README.md` and `docs/CLI_USAGE.md` in the same task.
- `docs/CLI_USAGE.md` should remain suitable for humans and AI agents that need to choose a read-only command without extra explanation.
- Prefer read-only CLI examples by default. Clearly mark commands that create, update, delete, send, upload, or mark data.
