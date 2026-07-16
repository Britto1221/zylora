import { redirect } from "next/navigation";
export default async function PortalRoot({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const { tenantSlug } = await params;
  redirect(`/portal/${tenantSlug}/dashboard`);
}
