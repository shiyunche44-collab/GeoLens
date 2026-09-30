"""Architecture snapshot for milestone reviews (docs/architecture.md §8.2).

uv run python scripts/arch_report.py > arch-report.md
"""

import os
from pathlib import Path

import grimp

os.environ.setdefault("GEOLENS_CELERY_EAGER", "true")

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from geolens.app.bootstrap import MODULES, load_all
from geolens.core.db import Base, get_engine

API = Path(__file__).resolve().parents[1]
REPO = API.parents[1]

# Evolution triggers (docs/architecture.md): metric -> threshold
TRIGGERS = {"fact rows (mentions + citations)": 50_000_000}


def loc(path: Path) -> int:
    return sum(len(p.read_text(encoding="utf-8").splitlines()) for p in path.rglob("*.py"))


def main() -> None:
    load_all()
    graph = grimp.build_graph("geolens")
    print("# GeoLens architecture report\n")

    print("## Modules\n")
    print("| module | LoC | tables | reaches (transitively, via public) |")
    print("|---|---|---|---|")
    for m in MODULES:
        pkg = f"geolens.modules.{m}"
        deps = sorted(
            {
                other
                for other in MODULES
                if other != m
                and graph.chain_exists(
                    importer=pkg, imported=f"geolens.modules.{other}", as_packages=True
                )
            }
        )
        tables = sorted(
            t.name
            for mp in Base.registry.mappers
            if mp.class_.__module__.startswith(pkg + ".")
            for t in [mp.local_table]
        )
        print(
            f"| {m} | {loc(API / 'geolens' / 'modules' / m)} | {', '.join(tables)} | "
            f"{', '.join(deps) or '—'} |"
        )

    print("\n## ADRs\n")
    for adr in sorted((REPO / "docs" / "adr").glob("[0-9]*.md")):
        status = next(
            (
                ln.split(":", 1)[1].strip()
                for ln in adr.read_text("utf-8").splitlines()
                if ln.lower().startswith("- status")
            ),
            "?",
        )
        print(f"- {adr.stem} — {status}")

    print("\n## Evolution triggers\n")
    try:
        with get_engine().connect() as conn:
            rows = sum(
                conn.execute(select(func.count()).select_from(Base.metadata.tables[t])).scalar_one()
                for t in ("mentions", "citations")
            )
        for name, limit in TRIGGERS.items():
            state = "**TRIGGERED — write an ADR**" if rows >= limit else "not reached"
            print(f"- {name}: {rows:,} / {limit:,} → {state}")
    except SQLAlchemyError:
        print("- database unreachable; trigger metrics skipped")


if __name__ == "__main__":
    main()
