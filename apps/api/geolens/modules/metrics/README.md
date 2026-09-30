# metrics

**职责**：GEO 指标口径的唯一定义与聚合——提及率、声量份额（SOV）、平均位次、引用率、GEO 可见度分。

**口径**：全部在 `definitions.py`（纯函数）。存储**可加的计数**（`metric_daily`），比率在读取时推导，因此任意时间窗口 / 引擎组合都能正确聚合。比率带 Wilson 95% 置信区间。
**修改口径 = 更新 `tests/golden/metrics_*.json` + 写 ADR。**

**对外接口（`public.py`）**：`get_project_metrics(project_id)`

**表**：`metric_daily`（project × brand × engine × day 唯一）

**演进**：P2 事实表迁 ClickHouse 后，本模块改为查询物化视图；增加告警（alerts 模块订阅指标变化）与报告导出。
