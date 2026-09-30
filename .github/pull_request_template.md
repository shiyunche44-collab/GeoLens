## 做了什么 / 为什么

<!-- 一两句话说明改动与动机；关联 Issue：#123 -->

## 影响范围

- 模块：<!-- identity / projects / collection / analysis / audit / metrics / web / infra -->
- 路线图阶段：<!-- P1 / P2 / P3（见 docs/roadmap.md，不在当前阶段范围内的改动请先讨论） -->

## 架构自检

- [ ] 跨模块只通过 `<module>.public` 调用，没有引用其他模块的 models / repository
- [ ] 新业务表带 `workspace_id`（WorkspaceScopedMixin），跨模块引用不建外键
- [ ] 外部付费调用经过 `identity.public.record_usage` 记账
- [ ] 改了 `public.py` 接口 / 表结构 / 指标口径 / 分析输出？→ 已说明兼容性（并升级 `ANALYZER_VERSION` / 更新 golden）
- [ ] 改了架构规则文件（`.importlinter`、`tests/architecture`、`metrics/definitions.py`、CI 等）？→ 已附 ADR（`docs/adr/`）
- [ ] 临时偏离架构？→ 已登记到 `docs/tech-debt.md`
- [ ] 本地 `make check` 通过

## 验证

<!-- 如何验证：测试、截图、make demo 输出等 -->
