import createClient from "openapi-fetch";

import type { components, paths } from "./schema";

/** Typed client generated from apps/api/openapi.json — never hand-write API types. */
export const api = createClient<paths>({ baseUrl: "/api" });

export type Schemas = components["schemas"];

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: unknown,
  ) {
    super(typeof detail === "object" && detail && "detail" in detail ? String(detail.detail) : `HTTP ${status}`);
  }
}

export async function unwrap<T>(req: Promise<{ data?: T; error?: unknown; response: Response }>): Promise<T> {
  const { data, error, response } = await req;
  if (error !== undefined || data === undefined) throw new ApiError(response.status, error);
  return data;
}
