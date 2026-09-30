# identity

**职责**：租户根（workspace）、用户与成员（P2）、API Key（P2）、配额与用量计量（usage_ledger）。

**对外接口（`public.py`）**
- `ensure_default_workspace()`：单租户 MVP 的默认工作区
- `record_usage(kind, units, cost_usd, meta)`：所有外部付费调用必须记账
- `workspace_scope`：FastAPI 依赖，把请求的工作区放进租户上下文

**表**：`workspaces`（全局表）、`usage_ledger`

**演进**：P2 增加 users / memberships / api_keys，`workspace_scope` 改为从认证信息解析并校验成员关系；开启 Postgres RLS。
