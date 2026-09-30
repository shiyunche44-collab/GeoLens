"use client";

import Link from "next/link";
import { useState } from "react";

import { Button, Card, ErrorText, Input } from "@/lib/ui";

import { useCreateProject, useProjects } from "./hooks";

export function ProjectList() {
  const projects = useProjects();
  const create = useCreateProject();
  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");

  return (
    <>
      <Card title="新建项目">
        <form
          className="flex flex-col gap-2 sm:flex-row"
          onSubmit={(e) => {
            e.preventDefault();
            create.mutate({ name, primary_domain: domain || null }, { onSuccess: () => setName("") });
          }}
        >
          <Input placeholder="项目名称，例如：GeoLens 品牌监测" value={name} onChange={(e) => setName(e.target.value)} required />
          <Input placeholder="主域名（可选）" value={domain} onChange={(e) => setDomain(e.target.value)} />
          <Button type="submit" disabled={create.isPending}>
            创建
          </Button>
        </form>
        <ErrorText error={create.error} />
      </Card>

      <Card title="项目">
        {projects.isLoading && <p className="text-sm text-muted">加载中…</p>}
        <ErrorText error={projects.error} />
        {projects.data?.length === 0 && <p className="text-sm text-muted">还没有项目。</p>}
        <ul className="divide-y divide-line">
          {projects.data?.map((p) => (
            <li key={p.id} className="flex items-center justify-between py-3">
              <div>
                <Link href={`/projects/${p.id}`} className="font-medium hover:underline">
                  {p.name}
                </Link>
                <p className="text-xs text-muted">
                  {p.brands.length} 个品牌 · {p.prompts.length} 个 Prompt
                </p>
              </div>
              <Link href={`/projects/${p.id}/visibility`} className="text-sm text-accent hover:underline">
                可见度看板
              </Link>
            </li>
          ))}
        </ul>
      </Card>
    </>
  );
}
