"""Registered audit rules. Add a rule: implement AuditRule, append to RULES,
add fixtures + cases in tests/contract/test_audit_rules.py (/new-audit-rule skill)."""

from geolens.modules.audit.rules.base import AuditRule, Finding, SiteContext
from geolens.modules.audit.rules.json_ld import JsonLdRule
from geolens.modules.audit.rules.llms_txt import LlmsTxtRule
from geolens.modules.audit.rules.robots_ai_bots import RobotsAiBotsRule

__all__ = ["RULES", "AuditRule", "Finding", "SiteContext", "run_all", "score"]

RULES: list[AuditRule] = [RobotsAiBotsRule(), LlmsTxtRule(), JsonLdRule()]

PENALTY = {"error": 25, "warn": 10, "info": 0}


def run_all(ctx: SiteContext) -> list[Finding]:
    return [f for rule in RULES for f in rule.evaluate(ctx)]


def score(findings: list[Finding]) -> int:
    return max(0, 100 - sum(PENALTY[f.severity] for f in findings))
