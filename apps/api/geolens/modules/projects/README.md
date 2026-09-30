# projects

**职责**：定义"监测什么"——项目、自有品牌与竞品（别名、域名）、Prompt（用户会向 AI 提的问题）。

**对外接口（`public.py`）**
- `get_snapshot(project_id) -> ProjectSnapshot`：品牌与 Prompt 的只读 DTO，供 collection / analysis 使用

**表**：`projects`、`brands`、`prompts`

**演进**：P1 后期增加 prompt_set / topic 分组、Prompt 批量导入与 AI 辅助生成；P2 增加意图分类与搜索量估算。
