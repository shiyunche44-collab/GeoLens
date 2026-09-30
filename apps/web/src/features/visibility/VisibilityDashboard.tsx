"use client";

import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { api, unwrap } from "@/lib/api/client";
import { Badge, Card, ErrorText, pct } from "@/lib/ui";

export function VisibilityDashboard({ projectId }: { projectId: string }) {
  const metrics = useQuery({
    queryKey: ["metrics", projectId],
    queryFn: () => unwrap(api.GET("/projects/{project_id}/metrics", { params: { path: { project_id: projectId } } })),
  });
  const [engine, setEngine] = useState("all");

  const engines = useMemo(() => [...new Set(metrics.data?.summary.map((m) => m.engine_id))].sort(), [metrics.data]);
  const rows = (metrics.data?.summary ?? [])
    .filter((m) => m.engine_id === engine)
    .sort((a, b) => b.visibility_score - a.visibility_score);

  return (
    <Card
      title="AI 可见度"
      actions={
        <div className="flex gap-1">
          {engines.map((e) => (
            <button
              key={e}
              onClick={() => setEngine(e)}
              className={`rounded px-2 py-1 text-xs ${e === engine ? "bg-accent text-white" : "bg-muted-bg text-muted"}`}
            >
              {e === "all" ? "全部引擎" : e}
            </button>
          ))}
        </div>
      }
    >
      <ErrorText error={metrics.error} />
      {metrics.data && rows.length === 0 && <p className="text-sm text-muted">暂无数据：先在项目页运行一次采集。</p>}
      {rows.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm tabular-nums">
            <thead className="text-left text-xs text-muted">
              <tr>
                <th className="py-2">品牌</th>
                <th className="text-right">可见度分</th>
                <th className="text-right">提及率（95% CI）</th>
                <th className="text-right">声量份额</th>
                <th className="text-right">平均位次</th>
                <th className="text-right">引用率</th>
                <th className="text-right">样本 n</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {rows.map((m) => (
                <tr key={m.brand_id}>
                  <td className="py-2">
                    {m.brand_name} {m.is_competitor ? <Badge tone="warn">竞品</Badge> : <Badge tone="ok">自有</Badge>}
                  </td>
                  <td className="text-right font-semibold">{m.visibility_score.toFixed(1)}</td>
                  <td className="text-right">
                    {pct(m.mention_rate.value)}{" "}
                    <span className="text-xs text-muted">
                      ({pct(m.mention_rate.ci_low)}–{pct(m.mention_rate.ci_high)})
                    </span>
                  </td>
                  <td className="text-right">{pct(m.share_of_voice)}</td>
                  <td className="text-right">{m.avg_position?.toFixed(2) ?? "—"}</td>
                  <td className="text-right">{pct(m.citation_rate.value)}</td>
                  <td className="text-right text-muted">{m.mention_rate.n}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="mt-4 text-xs text-muted">
        口径见 docs/architecture.md「指标口径」。AI 答案具有随机性，比率均为多次采样的统计值，请结合置信区间与样本量解读。
      </p>
    </Card>
  );
}
