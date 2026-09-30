"use client";

import { useState } from "react";

import { Badge, Button, Card, ErrorText, Input } from "@/lib/ui";

import { useEngines, useRun, useStartRun } from "./hooks";

const REGION = { cn: "国内", global: "海外" } as const;

export function RunPanel({ projectId }: { projectId: string }) {
  const engines = useEngines();
  const start = useStartRun(projectId);
  const [selected, setSelected] = useState<string[]>([]);
  const [samples, setSamples] = useState(3);
  const [runId, setRunId] = useState<string | null>(null);
  const run = useRun(runId);

  const toggle = (id: string) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));

  return (
    <Card title="采集运行">
      <div className="mb-3 flex flex-wrap gap-3">
        {engines.data?.map((e) => (
          <label key={e.id} className="flex items-center gap-1.5 text-sm">
            <input type="checkbox" checked={selected.includes(e.id)} onChange={() => toggle(e.id)} />
            {e.display_name}
            <Badge>{REGION[e.region as keyof typeof REGION] ?? e.region}</Badge>
            {e.fidelity !== "ui" && <Badge tone="info">{e.fidelity}</Badge>}
          </label>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted">每个 Prompt 采样</span>
        <div className="w-20">
          <Input type="number" min={1} max={20} value={samples} onChange={(e) => setSamples(Number(e.target.value))} />
        </div>
        <span className="text-sm text-muted">次</span>
        <Button
          disabled={!selected.length || start.isPending}
          onClick={() => start.mutate({ engines: selected, samples_per_prompt: samples }, { onSuccess: (r) => setRunId(r.id) })}
        >
          开始采集
        </Button>
      </div>
      <ErrorText error={start.error ?? engines.error} />
      {run.data && (
        <p className="mt-3 text-sm">
          运行 <code className="text-xs">{run.data.id.slice(0, 8)}</code>：
          <Badge tone={run.data.status === "completed" ? "ok" : run.data.status === "failed" ? "error" : "info"}>
            {run.data.status}
          </Badge>{" "}
          {run.data.done_tasks + run.data.failed_tasks}/{run.data.total_tasks} 个任务
          {run.data.failed_tasks > 0 && `（失败 ${run.data.failed_tasks}）`}
        </p>
      )}
    </Card>
  );
}
