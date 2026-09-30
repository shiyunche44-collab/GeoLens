import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "GeoLens",
  description: "GEO analytics: brand visibility in generative AI engines",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen antialiased">
        <nav className="border-b border-line bg-surface">
          <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
            <Link href="/projects" className="font-semibold">
              GeoLens
            </Link>
            <Link href="/projects" className="text-sm text-muted hover:text-ink">
              项目
            </Link>
            <Link href="/audits" className="text-sm text-muted hover:text-ink">
              站点审计
            </Link>
          </div>
        </nav>
        <main className="mx-auto max-w-6xl space-y-6 px-4 py-6">
          <Providers>{children}</Providers>
        </main>
      </body>
    </html>
  );
}
