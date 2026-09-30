import asyncio
import hashlib
import logging
import uuid
from datetime import UTC, datetime

from geolens.core import events
from geolens.core.config import get_settings
from geolens.core.db import session_scope, utcnow
from geolens.core.queue import enqueue
from geolens.core.storage import get_storage
from geolens.core.tenancy import current_workspace_id
from geolens.modules.collection.adapters import registry
from geolens.modules.collection.adapters.base import QueryRequest
from geolens.modules.collection.events import RESPONSE_COLLECTED, RUN_COMPLETED
from geolens.modules.collection.models import QueryTask, Response, Run
from geolens.modules.collection.repository import (
    QueryTaskRepository,
    ResponseRepository,
    RunRepository,
)
from geolens.modules.collection.schemas import EngineOut, ResponseOut, RunCreate, RunOut
from geolens.modules.identity import public as identity
from geolens.modules.projects import public as projects

log = logging.getLogger(__name__)

COLLECT_TASK = "collection.collect"


class RunNotFoundError(LookupError):
    pass


class UnknownEngineError(ValueError):
    pass


def list_engines() -> list[EngineOut]:
    out: list[EngineOut] = []
    for eid in registry.available_ids():
        a = registry.get(eid)
        out.append(
            EngineOut(
                id=eid,
                display_name=a.display_name,
                region=a.region,
                mode=a.mode,
                fidelity=a.fidelity,
            )
        )
    return out


def idempotency_key(
    project_id: uuid.UUID,
    prompt_id: uuid.UUID,
    engine_id: str,
    locale: str,
    sample_idx: int,
    bucket: str,
) -> str:
    """Same (prompt, engine, locale, sample) in the same bucket is collected once.

    Scheduled runs use the UTC date as bucket (dedupes double-fires); manual runs
    use the run id (every manual run is fresh, retries are still deduped).
    """
    raw = f"{project_id}|{prompt_id}|{engine_id}|{locale}|{sample_idx}|{bucket}"
    return hashlib.sha256(raw.encode()).hexdigest()


def plan_run(project_id: uuid.UUID, data: RunCreate, trigger: str = "manual") -> RunOut:
    snapshot = projects.get_snapshot(project_id)
    available = set(registry.available_ids())
    unknown = [e for e in data.engines if e not in available]
    if unknown:
        raise UnknownEngineError(f"engines not available: {unknown}")
    samples = data.samples_per_prompt or get_settings().default_samples_per_prompt

    with session_scope() as s:
        run = RunRepository(s).add(
            Run(
                project_id=project_id,
                trigger=trigger,
                engines=data.engines,
                samples_per_prompt=samples,
            )
        )
        bucket = datetime.now(UTC).date().isoformat() if trigger == "schedule" else str(run.id)
        tasks: list[QueryTask] = []
        for prompt in snapshot.prompts:
            locale = prompt.locale or snapshot.default_locale
            for engine_id in data.engines:
                for i in range(samples):
                    tasks.append(
                        QueryTask(
                            run_id=run.id,
                            prompt_id=prompt.id,
                            prompt_text=prompt.text,
                            engine_id=engine_id,
                            locale=locale,
                            sample_idx=i,
                            idempotency_key=idempotency_key(
                                project_id, prompt.id, engine_id, locale, i, bucket
                            ),
                        )
                    )
        repo = QueryTaskRepository(s)
        seen = repo.existing_keys([t.idempotency_key for t in tasks])
        tasks = [t for t in tasks if t.idempotency_key not in seen]
        for t in tasks:
            repo.add(t)
        run.total_tasks = len(tasks)
        run.status = "running" if tasks else "completed"
        dispatch = [(t.id, registry.get(t.engine_id).region) for t in tasks]
        run_id = run.id

    # Enqueue only after commit so workers always see the rows.
    ws = current_workspace_id()
    for task_id, region in dispatch:
        enqueue(COLLECT_TASK, workspace_id=ws, queue=f"collect.{region}", task_id=str(task_id))
    return get_run(run_id)


def collect(task_id: uuid.UUID) -> None:
    """Execute one QueryTask: ask the engine, snapshot the raw answer, emit an event."""
    with session_scope() as s:
        task = QueryTaskRepository(s).get(task_id)
        if task is None or task.status == "done":
            return  # idempotent: redelivered message
        task.attempts += 1
        req = QueryRequest(prompt=task.prompt_text, locale=task.locale, sample_idx=task.sample_idx)
        engine_id, run_id, prompt_id = task.engine_id, task.run_id, task.prompt_id

    adapter = registry.get(engine_id)
    ws = current_workspace_id()
    try:
        raw = asyncio.run(adapter.query(req))
        parsed = adapter.parse(raw)
    except Exception as e:
        log.exception("collect failed task=%s engine=%s", task_id, engine_id)
        with session_scope() as s:
            t = QueryTaskRepository(s).get(task_id)
            assert t is not None
            t.status, t.error = "failed", repr(e)[:2000]
            run = RunRepository(s).bump(run_id, failed=True)
            project_id, finished = run.project_id, _maybe_finish(run)
        if finished:
            events.publish(
                RUN_COMPLETED, workspace_id=ws, run_id=str(run_id), project_id=str(project_id)
            )
        return

    identity.record_usage(
        f"engine_query:{engine_id}",
        units=raw.units,
        cost_usd=raw.cost_usd,
        meta={"model": raw.model, "latency_ms": raw.latency_ms},
    )
    day = utcnow().date().isoformat()
    raw_uri = get_storage().put_json(
        f"raw/{ws}/{engine_id}/{day}/{task_id}.json",
        {
            "engine_id": engine_id,
            "request": req.__dict__,
            "model": raw.model,
            "latency_ms": raw.latency_ms,
            "payload": raw.payload,
        },
    )
    with session_scope() as s:
        t = QueryTaskRepository(s).get(task_id)
        assert t is not None
        t.status = "done"
        run = RunRepository(s).get(run_id)
        assert run is not None
        response = ResponseRepository(s).add(
            Response(
                task_id=task_id,
                run_id=run_id,
                project_id=run.project_id,
                prompt_id=prompt_id,
                engine_id=engine_id,
                fidelity=adapter.fidelity,
                model=parsed.model,
                raw_uri=raw_uri,
                answer_text=parsed.text,
                latency_ms=raw.latency_ms,
                citations=[{"url": c.url, "title": c.title} for c in parsed.citations],
            )
        )
        response_id, project_id = response.id, run.project_id
        run = RunRepository(s).bump(run_id, failed=False)
        finished = _maybe_finish(run)

    events.publish(
        RESPONSE_COLLECTED,
        workspace_id=ws,
        response_id=str(response_id),
        project_id=str(project_id),
    )
    if finished:
        events.publish(
            RUN_COMPLETED, workspace_id=ws, run_id=str(run_id), project_id=str(project_id)
        )


def _maybe_finish(run: Run) -> bool:
    if run.status == "running" and run.done_tasks + run.failed_tasks >= run.total_tasks:
        run.status = "completed" if run.done_tasks else "failed"
        run.finished_at = utcnow()
        return True
    return False


def get_run(run_id: uuid.UUID) -> RunOut:
    with session_scope() as s:
        run = RunRepository(s).get(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        return RunOut.model_validate(run)


def list_run_responses(run_id: uuid.UUID) -> list[ResponseOut]:
    get_run(run_id)
    with session_scope() as s:
        return [ResponseOut.model_validate(r) for r in ResponseRepository(s).for_run(run_id)]


def get_response(response_id: uuid.UUID) -> ResponseOut:
    with session_scope() as s:
        r = ResponseRepository(s).get(response_id)
        if r is None:
            raise LookupError(response_id)
        return ResponseOut.model_validate(r)
