import type { NextConfig } from "next";

const apiUrl = process.env.GEOLENS_API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  // The browser talks to /api/*; Next proxies to the FastAPI service (no CORS needed).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/:path*` }];
  },
};

export default nextConfig;
