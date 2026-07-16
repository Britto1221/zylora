import { PortalShell } from "@/components/portal/PortalShell";
import { serverApi } from "@/lib/api/server";

export default async function PortalLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ tenantSlug: string }>;
}) {
  const { tenantSlug } = await params;
  const data = await serverApi<{ tenant: { id: string; name: string } }>(`/tenants/slug/${tenantSlug}`);
  return <PortalShell slug={tenantSlug} clientName={data.tenant.name}>{children}</PortalShell>;
}
