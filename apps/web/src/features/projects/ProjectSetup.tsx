"use client";

import { useState } from "react";

import { Badge, Button, Card, ErrorText, Input } from "@/lib/ui";

import { useAddBrand, useAddPrompt, useProject } from "./hooks";

const splitList = (s: string) =>
  s
    .split(/[,，]/)
    .map((x) => x.trim())
    .filter(Boolean);

export function ProjectSetup({ projectId }: { projectId: string }) {
  const project = useProject(projectId);
  const addBrand = useAddBrand(projectId);
  const addPrompt = useAddPrompt(projectId);
  const [brand, setBrand] = useState({ name: "", aliases: "", domains: "", competitor: false });
  const [prompt, setPrompt] = useState("");

  if (project.isLoading) return <p className="text-sm text-muted">加载中…</p>;
  if (!project.data) return <ErrorText error={project.error ?? "项目不存在"} />;
  const p = project.data;

  return (
    <>
      <h1 className="text-xl font-semibold">{p.name}</h1>

      <Card title="品牌与竞品">
        <ul className="mb-4 space-y-1 text-sm">
          {p.brands.map((b) => (
            <li key={b.id} className="flex flex-wrap items-center gap-2">
              <span className="font-medium">{b.name}</span>
              <Badge tone={b.is_competitor ? "warn" : "ok"}>{b.is_competitor ? "竞品" : "自有"}</Badge>
              {b.aliases?.length ? <span className="text-muted">别名：{b.aliases.join("、")}</span> : null}
              {b.domains?.length ? <span className="text-muted">域名：{b.domains.join("、")}</span> : null}
            </li>
          ))}
        </ul>
        <form
          className="grid gap-2 sm:grid-cols-[1fr_1fr_1fr_auto_auto]"
          onSubmit={(e) => {
            e.preventDefault();
            addBrand.mutate(
              {
                name: brand.name,
                aliases: splitList(brand.aliases),
                domains: splitList(brand.domains),
                is_competitor: brand.competitor,
              },
              { onSuccess: () => setBrand({ name: "", aliases: "", domains: "", competitor: false }) },
            );
          }}
        >
          <Input placeholder="品牌名" value={brand.name} onChange={(e) => setBrand({ ...brand, name: e.target.value })} required />
          <Input placeholder="别名（逗号分隔）" value={brand.aliases} onChange={(e) => setBrand({ ...brand, aliases: e.target.value })} />
          <Input placeholder="域名（逗号分隔）" value={brand.domains} onChange={(e) => setBrand({ ...brand, domains: e.target.value })} />
          <label className="flex items-center gap-1 text-sm">
            <input type="checkbox" checked={brand.competitor} onChange={(e) => setBrand({ ...brand, competitor: e.target.checked })} />
            竞品
          </label>
          <Button type="submit" disabled={addBrand.isPending}>
            添加
          </Button>
        </form>
        <ErrorText error={addBrand.error} />
      </Card>

      <Card title="Prompt（用户会向 AI 提的问题）">
        <ul className="mb-4 list-disc space-y-1 pl-5 text-sm">
          {p.prompts.map((q) => (
            <li key={q.id}>{q.text}</li>
          ))}
        </ul>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            addPrompt.mutate({ text: prompt }, { onSuccess: () => setPrompt("") });
          }}
        >
          <Input placeholder="例如：最好的 GEO 分析工具有哪些？" value={prompt} onChange={(e) => setPrompt(e.target.value)} required />
          <Button type="submit" disabled={addPrompt.isPending}>
            添加
          </Button>
        </form>
        <ErrorText error={addPrompt.error} />
      </Card>
    </>
  );
}
