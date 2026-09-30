"""Schema-level architecture rules, checked against the live ORM metadata."""

import pytest
from sqlalchemy import Table

from geolens.core.db import Base

# Tables allowed to exist without workspace_id. Adding one requires an ADR.
GLOBAL_TABLES = {"workspaces"}
# Fact tables must record which analyzer produced them (ADR-0003).
VERSIONED_FACT_TABLES = {"analyzed_responses", "mentions", "citations"}


def _owner_module(table: Table) -> str:
    for mapper in Base.registry.mappers:
        if mapper.local_table is table:
            return mapper.class_.__module__.split(".")[2]  # geolens.modules.<name>.models
    raise AssertionError(f"table {table.name} has no mapped class")


TABLES = list(Base.metadata.sorted_tables)


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_business_tables_are_tenant_scoped(table: Table) -> None:
    if table.name in GLOBAL_TABLES:
        return
    col = table.columns.get("workspace_id")
    assert col is not None, f"{table.name}: missing workspace_id (use WorkspaceScopedMixin)"
    assert not col.nullable, f"{table.name}.workspace_id must be NOT NULL"
    assert any("workspace_id" in idx.columns for idx in table.indexes), (
        f"{table.name}.workspace_id must be indexed"
    )


@pytest.mark.parametrize("table", TABLES, ids=lambda t: t.name)
def test_no_foreign_keys_across_modules(table: Table) -> None:
    """Cross-module references are plain UUIDs so modules can later split into services."""
    owner = _owner_module(table)
    for fk in table.foreign_keys:
        target = _owner_module(fk.column.table)
        assert target == owner, (
            f"{table.name}.{fk.parent.name} -> {fk.column.table.name}: FK crosses module "
            f"boundary ({owner} -> {target}); store the id as a plain Uuid column instead"
        )


def test_fact_tables_record_analyzer_version() -> None:
    for name in VERSIONED_FACT_TABLES:
        col = Base.metadata.tables[name].columns.get("analyzer_version")
        assert col is not None and not col.nullable, f"{name} needs analyzer_version"


def test_responses_always_point_to_a_raw_snapshot() -> None:
    col = Base.metadata.tables["responses"].columns["raw_uri"]
    assert not col.nullable
