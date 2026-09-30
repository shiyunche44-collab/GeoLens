# 0006. 租户就绪的数据模型与用量计量

- Status: accepted
- Date: 2026-09-30

## 背景

产品先给自用或单团队使用，之后做 SaaS。等到上线后再给所有表补 `workspace_id` 和计费数据，迁移成本和风险都很高。

## 决策

- 除 `workspaces` 外，所有业务表都混入 `WorkspaceScopedMixin`（`workspace_id` 非空且有索引），由架构测试检查。
- 租户上下文放在 ContextVar 里：HTTP 请求由 `identity.public.workspace_scope` 设置（MVP 没有请求头时使用默认工作区），Celery 任务由 `tenant_task` 设置。
- 查询一律通过 `WorkspaceRepository`，它会自动加上租户过滤条件；没有租户上下文时直接抛异常（有单元测试和集成隔离测试）。
- 跨模块引用只存 UUID，不建外键（有架构测试），保证模块以后可以拆分。
- 所有付费外部调用都通过 `identity.public.record_usage` 写入 `usage_ledger`。它既是成本看板的数据源，也是 P2 配额和计费的数据源。
- P2：开启 Postgres RLS 作为第二道防线；`workspace_scope` 改为根据认证信息解析工作区并校验成员关系。

## 后果

- P1 在单租户下几乎没有额外成本，P2 升级时不需要改表结构。
- 目前任何人都能通过 `X-Workspace-Id` 请求头切换工作区。这在单租户、内网部署下可以接受，**对外开放之前必须接入认证**（这是 P2 出口标准"租户隔离渗透测试通过"的一部分）。
