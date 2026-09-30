# collection

**职责**：把"项目 × Prompt × 引擎 × 采样次数"展开成采集任务，分发到区域队列（`collect.cn` / `collect.global`），调用引擎适配器，**先存原始快照再落库**，发出事件。

**对外接口（`public.py`）**
- 事件：`RESPONSE_COLLECTED`（response_id, project_id）、`RUN_COMPLETED`（run_id, project_id）
- `get_response(response_id) -> ResponseOut`

**表**：`runs`、`query_tasks`（幂等键唯一）、`responses`（`raw_uri` 非空）

**新增引擎**：
- OpenAI 兼容接口 → 在 `adapters/openai_compatible.py` 的 `SPECS` 加一行
- 其他 → 在 `adapters/` 新建实现 `EngineAdapter` 协议的类，并在 `adapters/__init__.py` 注册
- 两种情况都**必须**在 `tests/fixtures/engines/<engine_id>.json` 提供录制的响应夹具，契约测试会自动覆盖（使用 `/new-engine-adapter` skill）

**演进**：P1 增加 schedules（Celery Beat）、按引擎令牌桶限流、SERP 型适配器（Google AI Overviews）；P2 改为区域采集 Agent 拉模式、浏览器采集模式。
