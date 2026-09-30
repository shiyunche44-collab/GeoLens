from urllib.robotparser import RobotFileParser

from geolens.modules.audit.rules.base import AI_BOTS, Category, Finding, SiteContext


class RobotsAiBotsRule:
    """Are AI crawlers allowed by robots.txt — and not silently blocked by a WAF?"""

    id = "access.robots_ai_bots"
    category: Category = "access"

    def evaluate(self, ctx: SiteContext) -> list[Finding]:
        findings: list[Finding] = []
        if ctx.robots_txt is None:
            findings.append(
                Finding(self.id, self.category, "info", "未找到 robots.txt，AI 爬虫默认可访问")
            )
        else:
            parser = RobotFileParser()
            parser.parse(ctx.robots_txt.splitlines())
            blocked = [bot for bot in AI_BOTS if not parser.can_fetch(bot, ctx.url)]
            if blocked:
                findings.append(
                    Finding(
                        self.id,
                        self.category,
                        "warn",
                        f"robots.txt 屏蔽了 AI 爬虫：{', '.join(blocked)}",
                        "如果希望被 AI 答案引用，请为对应爬虫放行（至少放行搜索/浏览类爬虫）",
                    )
                )
        if ctx.homepage_status and ctx.homepage_status < 400:
            waf_blocked = [b for b, st in ctx.bot_probe_status.items() if st >= 400]
            if waf_blocked:
                findings.append(
                    Finding(
                        self.id,
                        self.category,
                        "error",
                        f"使用 AI 爬虫 UA 访问首页被拒绝（WAF/CDN 拦截）：{', '.join(waf_blocked)}",
                        "检查 Cloudflare/WAF 的 Bot 防护规则，为已验证的 AI 爬虫放行",
                    )
                )
        return findings
