---
name: new-audit-rule
description: Add a site GEO audit rule to GeoLens (e.g. SSR vs CSR content, FAQ schema, author/date E-E-A-T signals, sitemap freshness). Use when the user asks to check/detect/audit something about a website's AI-friendliness.
---

# Add an audit rule

Rules live in `apps/api/geolens/modules/audit/rules/` and are **pure functions** of a
`SiteContext` (no network, no DB — enforced by the `pure-domain` import contract).

1. **Data first**: if the rule needs data the crawler doesn't fetch yet, extend
   `SiteContext` in `rules/base.py` and fill it in `audit/crawler.py` (the only place allowed
   to use the network; every fetched URL must go through `_get`, which applies the SSRF guard).
2. **Rule**: create `rules/<name>.py` with a class exposing `id = "<category>.<name>"`,
   `category` (`access | extractability | trust | freshness`) and
   `evaluate(ctx) -> list[Finding]`. Messages and recommendations are user-facing Chinese copy;
   recommendations must be actionable.
3. **Register**: append an instance to `RULES` in `rules/__init__.py`.
4. **Tests** (CI fails without them): in `apps/api/tests/contract/test_audit_rules.py`
   - make sure the shared `GOOD` context passes your rule (extend `GOOD` if needed),
   - add a `BAD_CASES["<rule id>"] = (context, expected_worst_severity)` entry,
   - add a focused test for any tricky parsing.
5. Scoring weights live in `rules/__init__.py` (`PENALTY`); changing them needs an ADR.
6. `make arch-check && make test`, then update `audit/README.md` and the rule list in
   `docs/architecture.md` §4.2.
