# 0004. 先用 PostgreSQL，存可加计数；达到阈值再引入 ClickHouse

- Status: accepted
- Date: 2026-09-30

## 背景

GEO 指标是时间序列分析（按品牌、引擎、日期、主题切片）。P1 数据量小，而过早引入 OLAP 会增加运维和同步的复杂度。

## 决策

- P1 只用 PostgreSQL。事实表（`analyzed_responses`、`mentions`、`citations`）只追加写入，结构可以直接迁移到 ClickHouse。
- `metric_daily` 存储**可加计数**（n_responses、n_mentioned、n_cited、position_sum、total_brand_mentions），比率（提及率、SOV、平均位次、引用率、可见度分）在读取时由 `metrics/definitions.py` 推导。这样任意时间窗口和引擎组合都能正确聚合，不会出现"比率的平均"这类错误。
- 比率附带 Wilson 95% 置信区间和样本量：LLM 答案是随机样本。
- 指标口径只在 `metrics/definitions.py` 里定义，并由手算的 golden 测试锁定。
- **触发器**：mentions + citations 超过 5000 万行，或看板 P95 超过 2s，就写 ADR 引入 ClickHouse（通过 CDC 或事件同步）。

## 后果

- P1 运维最简单。
- 重算由 Postgres 咨询锁按项目串行化，保证正确；它的性能问题已登记为技术债 #1。
