"""Every registered audit rule must declare good/bad cases here — enforced below."""

import dataclasses

import pytest

from geolens.modules.audit import rules
from geolens.modules.audit.rules.base import SiteContext

GOOD_HTML = """<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[{"@type":"Organization"},{"@type":"WebSite"}]}
</script>"""

GOOD = SiteContext(
    url="https://good.example.com/",
    robots_txt="User-agent: *\nAllow: /\n",
    llms_txt="# Good Inc\n> What we do\n- [Docs](https://good.example.com/docs)\n",
    homepage_html=GOOD_HTML,
    homepage_status=200,
    bot_probe_status={"GPTBot": 200, "ClaudeBot": 200},
)

# rule id -> (bad context, expected worst severity)
BAD_CASES: dict[str, tuple[SiteContext, str]] = {
    "access.robots_ai_bots": (
        dataclasses.replace(GOOD, bot_probe_status={"GPTBot": 403, "ClaudeBot": 200}),
        "error",
    ),
    "access.llms_txt": (dataclasses.replace(GOOD, llms_txt=None), "warn"),
    "trust.json_ld": (dataclasses.replace(GOOD, homepage_html="<p>no data</p>"), "warn"),
}
SEVERITY_ORDER = {"info": 0, "warn": 1, "error": 2}


def test_rule_ids_are_unique_and_namespaced() -> None:
    ids = [r.id for r in rules.RULES]
    assert len(ids) == len(set(ids))
    for r in rules.RULES:
        assert r.id.startswith(f"{r.category}."), f"{r.id} must be prefixed by its category"


@pytest.mark.parametrize("rule", rules.RULES, ids=lambda r: r.id)
def test_rule_passes_good_site(rule: rules.AuditRule) -> None:
    assert all(f.severity == "info" for f in rule.evaluate(GOOD))


@pytest.mark.parametrize("rule", rules.RULES, ids=lambda r: r.id)
def test_rule_flags_bad_site(rule: rules.AuditRule) -> None:
    assert rule.id in BAD_CASES, f"add a bad case for {rule.id} in BAD_CASES"
    ctx, expected = BAD_CASES[rule.id]
    findings = rule.evaluate(ctx)
    assert findings and all(f.rule_id == rule.id for f in findings)
    worst = max(SEVERITY_ORDER[f.severity] for f in findings)
    assert worst == SEVERITY_ORDER[expected]


def test_robots_blocking_ai_bots_is_reported() -> None:
    ctx = dataclasses.replace(GOOD, robots_txt="User-agent: GPTBot\nDisallow: /\n")
    (finding,) = [f for f in rules.run_all(ctx) if f.rule_id == "access.robots_ai_bots"]
    assert finding.severity == "warn" and "GPTBot" in finding.message


def test_score() -> None:
    assert rules.score(rules.run_all(GOOD)) == 100
    ctx, _ = BAD_CASES["access.robots_ai_bots"]
    assert rules.score(rules.run_all(ctx)) == 75
