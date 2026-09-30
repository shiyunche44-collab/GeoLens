# 0002. Python（FastAPI + SQLAlchemy 同步 + Celery）作为后端技术栈

- Status: accepted
- Date: 2026-09-30

## 背景

核心工作量在采集（大量外部 HTTP 调用）、NLP/LLM 分析、爬虫和审计上，Python 在这些领域的生态最成熟。前端用 Next.js，通过 OpenAPI 共享契约。

## 决策

- **API**：FastAPI + Pydantic v2，路由用同步函数（在线程池里执行）。
- **数据访问**：SQLAlchemy 2（同步）+ psycopg3；迁移用 Alembic，CI 跑 `alembic check` 检查漂移。
- **任务**：Celery，Redis 作 broker。队列按职责和区域划分：`default`、`collect.cn`、`collect.global`、`analyze`、`audit`。
- **任务入队**：service 按任务名入队（`core.queue.enqueue`），不 import 自己模块的 `tasks`，避免循环依赖。
- **事件**：`core.events.publish/subscribe` 通过 Celery 任务投递，接口稳定，底层传输以后可以替换。
- **外部 I/O**：适配器的 `query` 用 async httpx，由任务通过 `asyncio.run` 调用。
- **测试**：`GEOLENS_CELERY_EAGER=true` 时任务同步执行，端到端测试不需要起 worker。

## 备选方案

- **全链路 async（asyncpg + async SQLAlchemy）**：和 Celery 的事件循环模型冲突（连接池会绑定在某个事件循环上），换来的收益在 P1 规模下不明显。等到出现 I/O 并发瓶颈时再评估（可以改用 arq/Dramatiq，或者只给采集 worker 换 async runtime）。
- **全栈 TypeScript**：团队门槛低，但 NLP 和爬虫生态弱。
- **Go**：采集性能好，但 LLM 和分析生态弱。

## 后果

- 代码简单，调试容易；采集的并发由 worker 进程数和队列控制。
- 采集任务里 `asyncio.run` 每次都会新建事件循环，单任务开销可以接受。P2 高并发采集时再评估。
