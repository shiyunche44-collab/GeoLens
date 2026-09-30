# GeoLens

**GEO（Generative Engine Optimization）检测分析平台**：监测品牌在 AI 生成式引擎答案中的可见度，并审计网站对 AI 的友好度。

- **AI 可见度监测**：把 Prompt 多次采样发给 DeepSeek、Kimi、通义、豆包、ChatGPT、Perplexity 等引擎，识别答案里的品牌提及、位次和引用来源，计算提及率、声量份额（SOV）、平均位次、引用率和 GEO 可见度分（均附置信区间），并和竞品对比
- **站点 GEO 审计**：AI 爬虫能否访问（robots.txt、WAF 拦截探测、llms.txt），结构化数据是否完整，最后给出评分和改进建议

> 架构：[`docs/architecture.md`](docs/architecture.md) · 路线图：[`docs/roadmap.md`](docs/roadmap.md) · 决策记录：[`docs/adr/`](docs/adr/) · 协作规则：[`CLAUDE.md`](CLAUDE.md)

## 仓库结构

```
apps/api     Python 3.12 · FastAPI · SQLAlchemy · Celery（模块化单体：identity / projects / collection / analysis / audit / metrics）
apps/web     Next.js 控制台（类型化 API 客户端由 apps/api/openapi.json 生成）
docs/        架构、路线图、ADR、技术债登记
.claude/     Claude Code hooks（依赖安装、架构守卫）与 skills（新增引擎/规则/模块/ADR 的标准做法）
.github/     CI（含架构与治理门禁）、PR/Issue 模板、CODEOWNERS
```

## 快速开始

依赖：Docker、[uv](https://docs.astral.sh/uv/)、Node 22、pnpm。

```bash
cp .env.example .env        # 可选：填入引擎 API Key（不填也能用 mock 引擎跑通）
make setup                  # 安装 API 与 web 依赖
make deps                   # Docker 启动 Postgres / Redis / MinIO
make migrate
make api                    # 终端 1：http://localhost:8000/docs
make worker                 # 终端 2
make web                    # 终端 3：http://localhost:3000
make demo                   # 用 mock 引擎跑一遍端到端流程并打印指标
```

也可以一条命令起整套服务：`make up`。

## 质量门禁

```bash
make check        # CI 同款：lint、类型、架构合约、测试、迁移、API 契约、前端构建
make arch-check   # 架构守卫（秒级）
make arch-report  # 里程碑架构复盘报告
```

违反架构规则（跨模块引用内部实现、业务表缺少 `workspace_id`、在规定位置之外直接调用外部 SDK、口径被改动……）会让 CI 失败。修改规则本身需要写 ADR。详见 [architecture §8](docs/architecture.md#8-架构治理让长期迭代不跑偏)。
