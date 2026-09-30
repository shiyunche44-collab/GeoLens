# analysis

**职责**：把引擎答案变成结构化事实——品牌提及（位次、上下文）、引用来源（URL、域名、是否属于某品牌）。

**核心**：`pipeline/` 是**纯函数**（不碰 DB/网络），输入 `AnalysisInput`，输出 `AnalysisResult`。修改任何步骤的输出时必须升级 `ANALYZER_VERSION` 并更新 golden 测试（`tests/golden/`）。

**对外接口（`public.py`）**
- 事件：`RESPONSE_ANALYZED`（response_id, project_id）
- `list_response_facts(project_id) -> list[ResponseFacts]`：给 metrics 用的观测数据

**表**：`analyzed_responses`（分母）、`mentions`、`citations`，均带 `analyzer_version`

**演进**：P1 增加 LLM 情感评判步骤（小模型 + 缓存）、歧义品牌 LLM 兜底；P2 增加引用源情报（按主题聚合高频域名）、pgvector 语义聚类。
