"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { api, unwrap } from "@/lib/api/client";
import { Badge, Button, Card, ErrorText, Input } from "@/lib/ui";

const SEVERITY_TONE = { info: "info", warn: "warn", error: "error" } as const;

export function AuditPanel() {
  const qc = useQueryClient();
  const [url, setUrl] = useState("");
  const audits = useQuery({
    queryKey: ["audits"],
    queryFn: () => unwrap(api.GET("/audits")),
    refetchInterval: (q) => (q.state.data?.some((a) => a.status === "pending") ? 2_000 : false),
  });
  const create = useMutation({
    mutationFn: (target: string) => unwrap(api.POST("/audits", { body: { url: target } })),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["audits"] }),
  });

  return (
    <>
      <Card title="站点 GEO 审计">
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            create.mutate(url);
          }}
        >
          <Input type="url" placeholder="https://www.example.com/" value={url} onChange={(e) => setUrl(e.target.value)} required />
          <Button type="submit" disabled={create.isPending}>
            开始审计
          </Button>
        </form>
        <ErrorText error={create.error} />
      </Card>

      <ErrorText error={audits.error} />
      {audits.data?.map((a) => (
        <Card
          key={a.id}
          title={<span className="break-all">{a.url}</span>}
          actions={a.status === "done" ? <span className="text-2xl font-semibold tabular-nums">{a.score}</span> : <Badge>{a.status}</Badge>}
        >
          {a.error && <ErrorText error={a.error} />}
          <ul className="space-y-2 text-sm">
            {a.findings.map((f, i) => (
              <li key={i}>
                <Badge tone={SEVERITY_TONE[f.severity as keyof typeof SEVERITY_TONE] ?? "neutral"}>{f.severity}</Badge>{" "}
                <span className="text-xs text-muted">{f.rule_id}</span> {f.message}
                {f.recommendation && <p className="ml-1 mt-0.5 text-xs text-muted">建议：{f.recommendation}</p>}
              </li>
            ))}
          </ul>
        </Card>
      ))}
    </>
  );
}
