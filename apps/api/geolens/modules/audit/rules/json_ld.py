import json
from typing import cast

from bs4 import BeautifulSoup

from geolens.modules.audit.rules.base import Category, Finding, SiteContext

RECOMMENDED_TYPES = {"Organization", "WebSite"}


def _types(node: object) -> set[str]:
    found: set[str] = set()
    if isinstance(node, list):
        for item in cast(list[object], node):
            found |= _types(item)
    elif isinstance(node, dict):
        d = cast(dict[str, object], node)
        t = d.get("@type")
        if isinstance(t, str):
            found.add(t)
        elif isinstance(t, list):
            found |= {x for x in cast(list[object], t) if isinstance(x, str)}
        for key in ("@graph", "mainEntity"):
            if key in d:
                found |= _types(d[key])
    return found


class JsonLdRule:
    """Structured data helps engines resolve *who* you are and trust what you say."""

    id = "trust.json_ld"
    category: Category = "trust"

    def evaluate(self, ctx: SiteContext) -> list[Finding]:
        if not ctx.homepage_html:
            return []
        soup = BeautifulSoup(ctx.homepage_html, "html.parser")
        blocks = soup.find_all("script", attrs={"type": "application/ld+json"})
        if not blocks:
            return [
                Finding(
                    self.id,
                    self.category,
                    "warn",
                    "首页没有 JSON-LD 结构化数据",
                    "至少添加 Organization 与 WebSite 的 JSON-LD",
                )
            ]
        findings: list[Finding] = []
        types: set[str] = set()
        for block in blocks:
            try:
                types |= _types(json.loads(block.get_text()))
            except json.JSONDecodeError:
                findings.append(
                    Finding(
                        self.id,
                        self.category,
                        "error",
                        "存在无法解析的 JSON-LD 块",
                        "修复 JSON 语法错误",
                    )
                )
        missing = RECOMMENDED_TYPES - types
        if missing:
            findings.append(
                Finding(
                    self.id,
                    self.category,
                    "info",
                    f"JSON-LD 缺少推荐类型：{', '.join(sorted(missing))}",
                    "补充 Organization（含 sameAs）与 WebSite",
                )
            )
        return findings
