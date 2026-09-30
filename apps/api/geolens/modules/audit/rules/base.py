"""Audit rule contract (ADR-0005). Rules are pure functions of a crawled SiteContext."""

from dataclasses import dataclass, field
from typing import Literal, Protocol

Severity = Literal["info", "warn", "error"]
Category = Literal["access", "extractability", "trust", "freshness"]

# Crawlers used by generative engines. Keep in sync with docs/architecture.md.
AI_BOTS: dict[str, str] = {
    "GPTBot": "OpenAI (training)",
    "OAI-SearchBot": "ChatGPT search",
    "ChatGPT-User": "ChatGPT browsing",
    "ClaudeBot": "Anthropic",
    "PerplexityBot": "Perplexity",
    "Google-Extended": "Gemini / Google AI",
    "Bytespider": "字节跳动（豆包）",
    "Baiduspider": "百度（文心）",
}


@dataclass(frozen=True)
class SiteContext:
    url: str
    robots_txt: str | None
    llms_txt: str | None
    homepage_html: str | None
    homepage_status: int | None
    bot_probe_status: dict[str, int] = field(default_factory=dict[str, int])


@dataclass(frozen=True)
class Finding:
    rule_id: str
    category: Category
    severity: Severity
    message: str
    recommendation: str | None = None


class AuditRule(Protocol):
    id: str
    category: Category

    def evaluate(self, ctx: SiteContext) -> list[Finding]: ...
