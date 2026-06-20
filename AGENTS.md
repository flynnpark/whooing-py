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
