import Link from "next/link";

import { ProjectSetup } from "@/features/projects/ProjectSetup";
import { RunPanel } from "@/features/runs/RunPanel";

export default async function ProjectPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <>
      <div className="flex justify-end">
        <Link href={`/projects/${id}/visibility`} className="text-sm text-accent hover:underline">
          查看可见度看板 →
        </Link>
      </div>
      <ProjectSetup projectId={id} />
      <RunPanel projectId={id} />
    </>
  );
}
