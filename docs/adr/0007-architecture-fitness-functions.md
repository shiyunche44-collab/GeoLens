# 0007. 用可执行的架构适应度函数守护架构

- Status: accepted
- Date: 2026-09-30

## 背景

项目会长期迭代，大量代码将通过 Claude Code 在很多个会话里完成。只写在文档里的架构规则会被遗忘，也会被一次次"顺手"突破。

## 决策

每条架构原则都对应一个自动检查（清单见 architecture §8.1），并分三道防线执行：

1. **写代码时**：
   - `CLAUDE.md` 写明硬性规则，模块 README 说明职责和接口
   - 项目 skills（`new-engine-adapter`、`new-audit-rule`、`new-module`、`new-adr`）提供标准做法
   - `make new-module` 脚手架
   - Claude Code 的 Stop hook：`apps/api` 有改动时自动运行 `make arch-check`，失败就把输出回灌给 Claude 修复
   - SessionStart hook：保证云端会话里依赖齐全
2. **合并时**：
   - CI 必过项：lint、类型、import 合约、架构测试、契约和 golden 测试、集成测试、迁移漂移检查、OpenAPI 与前端类型一致性、前端构建
   - governance 任务：改了规则文件却没有 ADR 就失败（`scripts/check-adr.sh`，可以用 `no-adr-needed` 标签豁免）；oasdiff 检测破坏性 API 变更（可以用 `api-breaking-approved` 标签豁免）
3. **演进时**：
   - 路线图的阶段门禁：每个阶段有"明确不做"清单和出口标准
   - 演进触发器：没到阈值不做，到了阈值必须写 ADR
   - 里程碑复盘时运行 `make arch-report`
   - 临时偏离登记到 `docs/tech-debt.md`

规则在代码量还小的时候就上线：骨架阶段和代码一起交付。

## 备选方案

- **只写文档，靠人工评审**：不能规模化，对 AI 生成的代码尤其无效。
- **用 ArchUnit 之类的重型平台**：Python 生态里 import-linter 加 pytest 已经足够，成本也更低。

## 后果

- 违规在本地或 CI 就会暴露，不会等到重构时才发现。
- 规则本身也要演进：规则文件受 `CODEOWNERS` 和 ADR 门禁保护，放宽规则是一件显式、留痕的事。
- 需要维护这套检查本身。检查代码量不大，而且每条检查都做过反向验证：故意违规一次，确认它会失败。
