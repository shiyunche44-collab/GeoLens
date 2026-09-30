from geolens.modules.audit.rules.base import Category, Finding, SiteContext


class LlmsTxtRule:
    id = "access.llms_txt"
    category: Category = "access"

    def evaluate(self, ctx: SiteContext) -> list[Finding]:
        if not ctx.llms_txt or not ctx.llms_txt.strip():
            return [
                Finding(
                    self.id,
                    self.category,
                    "warn",
                    "未提供 /llms.txt",
                    "添加 /llms.txt，用 Markdown 概述站点与关键页面，方便 LLM 理解",
                )
            ]
        if not ctx.llms_txt.lstrip().startswith("#"):
            return [
                Finding(
                    self.id,
                    self.category,
                    "info",
                    "/llms.txt 存在但不是以 Markdown 标题开头",
                    "按 llms.txt 约定以 `# 站点名` 开头，并附简介与链接列表",
                )
            ]
        return []
