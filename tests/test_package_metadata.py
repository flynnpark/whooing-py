from __future__ import annotations

import tomllib
from importlib.metadata import version
from pathlib import Path

from whooing import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_package_versions_are_consistent() -> None:
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]

    assert project_version == __version__
    assert version("whooing-py") == __version__
