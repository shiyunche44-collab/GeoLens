"""Scaffold a new bounded-context module with the standard shape.

    uv run python scripts/new_module.py alerts

Creates geolens/modules/<name>/ and registers it in bootstrap.MODULES and in
both .importlinter module contracts. A new module is an architectural change:
write an ADR (docs/adr/) in the same PR.
"""

import re
import sys
from pathlib import Path

API = Path(__file__).resolve().parents[1]

FILES = {
    "__init__.py": "",
    "public.py": '"""Public interface of {name}. Other modules import ONLY this file."""\n',
    "api.py": (
        'from fastapi import APIRouter\n\nrouter = APIRouter(prefix="/{name}", tags=["{name}"])\n'
    ),
    "service.py": '"""Use cases of the {name} module."""\n',
    "repository.py": ("from geolens.core.repository import WorkspaceRepository  # noqa: F401\n"),
    "models.py": (
        "from geolens.core.db import Base, TimestampMixin  # noqa: F401\n"
        "from geolens.core.tenancy import WorkspaceScopedMixin  # noqa: F401\n"
    ),
    "schemas.py": "from pydantic import BaseModel  # noqa: F401\n",
    "README.md": (
        "# {name}\n\n**职责**：TODO\n\n**对外接口（`public.py`）**：TODO\n\n**表**：TODO\n\n"
        "**ADR**：docs/adr/NNNN-{name}-module.md\n"
    ),
}


def main(name: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        sys.exit("module name must be snake_case")
    target = API / "geolens" / "modules" / name
    if target.exists():
        sys.exit(f"{target} already exists")
    target.mkdir(parents=True)
    for fname, content in FILES.items():
        (target / fname).write_text(content.format(name=name), encoding="utf-8")

    boot = API / "geolens" / "app" / "bootstrap.py"
    src = boot.read_text(encoding="utf-8")
    boot.write_text(src.replace('"metrics"]', f'"metrics", "{name}"]', 1), encoding="utf-8")

    lint = API / ".importlinter"
    cfg = lint.read_text(encoding="utf-8")
    cfg = cfg.replace(
        "    geolens.modules.metrics\n",
        f"    geolens.modules.metrics\n    geolens.modules.{name}\n",
    )
    lint.write_text(cfg, encoding="utf-8")

    print(f"created {target.relative_to(API)} and registered it in bootstrap + .importlinter")
    print("next: write an ADR, wire the router in geolens/app/main.py, run `make check`")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
