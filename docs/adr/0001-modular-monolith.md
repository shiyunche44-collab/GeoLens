# 0001. 以模块化单体起步，按限界上下文划分模块

- Status: accepted
- Date: 2026-09-30

## 背景

GeoLens 要从自用工具演进为 SaaS 和开放平台。起步阶段只有一个团队，需求变化快；但采集（跨区域、出口 IP、并发）和分析（LLM 成本）将来确实会有独立扩缩的需要。

## 决策

- 采用一个 Python 包 `geolens` 的模块化单体。按限界上下文分为 `identity`、`projects`、`collection`、`analysis`、`audit`、`metrics` 六个模块。
- 同一份代码以两种进程角色运行：`api`（FastAPI）和 `worker`（Celery，按队列部署）。
- 模块之间只通过 `<module>/public.py`（门面函数 + DTO）和领域事件交互。只有 `geolens/app`（组合根）可以 import 所有模块。
- 模块内部分层：`api | tasks | public` → `service` → `repository` → `models` → 纯领域 → `schemas | events`。
- 由 import-linter 的 `top-layers`、`module-boundaries`、`module-layers` 三个合约强制执行。

## 备选方案

- **一开始就上微服务**：运维、部署、分布式事务的成本远高于当前收益，而且边界没稳定之前，拆错的代价很大。
- **不设边界的单体**：前期最快，但迭代半年后耦合会让拆分无法进行，也无法并行开发。

## 后果

- 本地开发和部署简单，一个仓库、一套测试。
- 以后拆服务时，只需把 `public.py` 换成 HTTP/gRPC 客户端、把事件换成消息总线，模块内部代码不用动。触发条件见 architecture §8.3。
- 代价：跨模块不能随手 join 表，需要通过 public 取 DTO。这是有意为之。
