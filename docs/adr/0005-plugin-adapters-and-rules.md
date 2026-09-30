# 0005. 引擎适配器与审计规则插件化

- Status: accepted
- Date: 2026-09-30

## 背景

要覆盖的引擎很多（国内：DeepSeek、豆包、Kimi、通义、文心、元宝；海外：ChatGPT、Perplexity、Gemini、Google AI Overviews……），而且会持续增加。审计规则也会持续扩充。

## 决策

- **引擎**：实现 `EngineAdapter` 协议（`query` / `parse`，声明 `region`、`mode`、`fidelity`），在注册表中登记；设置了凭据的引擎才会启用。
- 大多数厂商兼容 OpenAI 的 `/chat/completions` 接口，所以用一个 `OpenAICompatibleAdapter` 加 `EngineSpec` 配置覆盖它们，新增这类引擎只需加一行配置。
- `region` 决定采集队列（`collect.cn` / `collect.global`）；`fidelity` 标明答案和真实产品界面的接近程度，报表会展示。
- **审计规则**：实现 `AuditRule`（纯函数 `evaluate(SiteContext)`），加入 `RULES`。
- **契约测试**：适配器测试按注册表参数化，缺少录制夹具就失败；审计规则缺少反例用例就失败。
- `mode="browser"`（模拟用户界面采集）默认不做，启用前需要单独写 ADR，评估服务条款和合规风险。

## 后果

- 新增引擎或规则的成本低，而且不会漏测。
- 适配器必须上报用量（`units` / `cost_usd`），由 collection 统一记账。
