import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, unwrap, type Schemas } from "@/lib/api/client";

export const projectKeys = {
  all: ["projects"] as const,
  one: (id: string) => ["projects", id] as const,
};

export function useProjects() {
  return useQuery({ queryKey: projectKeys.all, queryFn: () => unwrap(api.GET("/projects")) });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: projectKeys.one(id),
    queryFn: () => unwrap(api.GET("/projects/{project_id}", { params: { path: { project_id: id } } })),
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Schemas["ProjectCreate"]) => unwrap(api.POST("/projects", { body })),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.all }),
  });
}

export function useAddBrand(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Schemas["BrandCreate"]) =>
      unwrap(api.POST("/projects/{project_id}/brands", { params: { path: { project_id: projectId } }, body })),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.one(projectId) }),
  });
}

export function useAddPrompt(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Schemas["PromptCreate"]) =>
      unwrap(api.POST("/projects/{project_id}/prompts", { params: { path: { project_id: projectId } }, body })),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.one(projectId) }),
  });
}
