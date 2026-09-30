import { VisibilityDashboard } from "@/features/visibility/VisibilityDashboard";

export default async function VisibilityPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <VisibilityDashboard projectId={id} />;
}
