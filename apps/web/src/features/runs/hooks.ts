import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, unwrap, type Schemas } from "@/lib/api/client";

export function useEngines() {
  return useQuery({ queryKey: ["engines"], queryFn: () => unwrap(api.GET("/engines")) });
}

export function useStartRun(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Schemas["RunCreate"]) =>
      unwrap(api.POST("/projects/{project_id}/runs", { params: { path: { project_id: projectId } }, body })),
    onSuccess: (run) => qc.setQueryData(["runs", run.id], run),
  });
}

export function useRun(runId: string | null) {
  return useQuery({
    queryKey: ["runs", runId],
    enabled: runId !== null,
    queryFn: () => unwrap(api.GET("/runs/{run_id}", { params: { path: { run_id: runId! } } })),
    refetchInterval: (q) => (q.state.data?.status === "running" || q.state.data?.status === "pending" ? 2_000 : false),
  });
}
