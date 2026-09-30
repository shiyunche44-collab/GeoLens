# 0003. 原始快照优先：先存原始响应，解析结果可重算

- Status: accepted
- Date: 2026-09-30

## 背景

引擎的响应格式会变，品牌识别和引用解析会不断改进，指标口径也可能调整。如果只保存解析后的结果，历史数据就无法用新逻辑重算，趋势会断档。LLM 调用有成本，也不可能重新采集历史数据。

## 决策

- 适配器的 `query` 返回服务端的原样 payload（`RawResponse.payload`）。collection 在落库之前，把它连同请求一起不可变地写入对象存储：`raw/{workspace}/{engine}/{date}/{task}.json`。
- `responses.raw_uri` 非空（有架构测试）。
- 分析是纯函数（`analysis/pipeline`），结果写入事实表时带上 `analyzer_version`。改变分析输出时必须升级版本号并更新 `tests/golden/analysis_cases.json`（有测试检查两者一致）。
- golden 测试把"录制的引擎响应 → adapter.parse → analyze → 期望事实"整条链路固定下来，从而证明快照可以重算。

## 后果

- 可以批量重跑历史快照（P1 后续提供 `reanalyze` 命令），口径升级后趋势不断档。
- 存储成本随采集量线性增长，P2 用对象存储生命周期策略做冷热分层。
- 快照里可能含有第三方内容，访问权限按租户隔离（key 前缀是 workspace）。
