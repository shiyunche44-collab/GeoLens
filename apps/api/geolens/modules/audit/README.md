# audit

**职责**：站点 GEO 审计——AI 爬虫能不能进来（robots.txt、WAF 拦截、llms.txt）、内容能不能被抽取（P1：SSR/CSR 差异、标题结构）、可信度信号（JSON-LD、作者/日期）、新鲜度与性能。

**结构**
- `crawler.py`：唯一允许联网的地方；带 SSRF 防护（仅 http(s)、仅公网 IP、逐跳校验重定向）
- `rules/`：**纯函数**规则，输入 `SiteContext`，输出 `Finding` 列表；`rules/__init__.py` 注册与打分

**对外接口（`public.py`）**：`get_audit(job_id)`

**表**：`audit_jobs`、`audit_findings`

**新增规则**：使用 `/new-audit-rule` skill——实现 `AuditRule`、加入 `RULES`、在 `tests/contract/test_audit_rules.py` 补正反用例。

**演进**：P1 多页面爬取（sitemap）、Playwright 渲染对比、FAQ/列表/表格结构；P2 AI 爬虫访问日志分析；DNS 重绑定防护。
