# GeoLens

GEO（Generative Engine Optimization）检测分析平台：监测品牌在 AI 生成式引擎（DeepSeek、豆包、Kimi、通义、ChatGPT、Perplexity……）答案中的可见度，并审计网站对 AI 的友好度。长期演进：工具 → SaaS → 开放平台。

- 架构总览：`docs/architecture.md`（**先读**）· 路线图与阶段边界：`docs/roadmap.md` · 决策记录：`docs/adr/`
- 后端 `apps/api`：Python 3.12 · FastAPI · SQLAlchemy 2 · Celery · Postgres · Redis · S3/MinIO（模块化单体）
- 前端 `apps/web`：Next.js App Router · TanStack Query · 由 `openapi.json` 生成的类型化客户端

## 常用命令（仓库根目录）

```bash
make check        # 合并门禁：lint + 类型 + 架构 + 测试 + 迁移 + API 契约 + 前端构建
make arch-check   # 架构守卫（秒级）：import 合约 + 架构测试
make test         # pytest（无 Postgres 时跳过集成测试）
make openapi      # 改了 API 后：重新生成 openapi.json 与前端类型
make api / make worker / make web / make demo
```

## 硬性架构规则（CI 自动检查，违反即失败）

1. **模块边界**：`geolens/modules/<m>/` 之间只能 import 对方的 `public.py`。不要 import 别的模块的 `models`/`service`/`repository`。
2. **模块内分层**：`api | tasks | public` → `service` → `repository` → `models` → 纯领域（`pipeline`/`rules`/`adapters`/`definitions`）→ `schemas`/`events`。只能向下依赖。
3. **core 不依赖 modules**；只有 `geolens/app`（组合根）能把所有模块接起来。
4. **租户**：业务表必须用 `WorkspaceScopedMixin`（`workspace_id` 非空且有索引）；查询一律通过 `WorkspaceRepository` 子类；跨模块引用只存 UUID，**不建外键**。
5. **外部依赖收口**：`httpx` 只在 `collection/adapters` 与 `audit/crawler`；`boto3` 只在 `core/storage`；`celery` 只在 `core/queue`。付费调用必须 `identity.public.record_usage(...)` 记账。
6. **原始快照优先**：采集结果先写对象存储（`responses.raw_uri` 非空），分析可从快照重算；事实表带 `analyzer_version`。
7. **纯函数核心**：`analysis/pipeline`、`metrics/definitions.py`、`audit/rules` 不得访问 DB/队列/存储。
8. **口径唯一**：指标公式只在 `metrics/definitions.py`；改分析输出要升级 `ANALYZER_VERSION` 并更新 `tests/golden/`。
9. **API 契约**：改了路由/Schema 必须 `make openapi` 并提交 `openapi.json` 与 `schema.d.ts`；前端只用生成的类型。
10. **前端边界**：`src/features/*` 之间不互相 import；`src/lib` 是最底层。

**要改规则本身**（`.importlinter`、`tests/architecture/`、`tests/golden/`、`metrics/definitions.py`、CI）→ **先写 ADR**（`/new-adr`），CI 的 governance 任务会检查。临时偏离 → 登记 `docs/tech-debt.md`。

## 常见改动配方（优先用 skills）

- 新增 AI 引擎 → `/new-engine-adapter`
- 新增审计规则 → `/new-audit-rule`
- 新增模块（限界上下文）→ `/new-module`（需要 ADR）
- 记录架构决策 → `/new-adr`

## 工作约定

- 先看目标模块的 `README.md`，改完同步更新它。
- 范围控制：只做 `docs/roadmap.md` 当前阶段范围内的事；"明确不做"清单里的需求先提出来，不要顺手实现。
- 新代码配测试：纯逻辑写单元/golden 测试，跨模块流程写 `tests/integration`（CI 有 Postgres）。
- Stop hook 会在 `apps/api` 有改动时自动跑 `make arch-check`，失败会把输出回灌——修复违规，不要绕过。
