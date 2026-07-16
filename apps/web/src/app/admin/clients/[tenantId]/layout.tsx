import { ClientTabs } from "@/components/admin/ClientTabs";
import { serverApi } from "@/lib/api/server";

type TenantResponse = {
  tenant: { id: string; name: string; slug: string; industry: string };
};

export default async function ClientLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ tenantId: string }>;
}) {
  const { tenantId } = await params;
  let client: TenantResponse | null = null;
  try {
    client = await serverApi<TenantResponse>(`/tenants/${tenantId}`);
  } catch {
    client = null;
  }
  return (
    <div className="page">
      <header style={{ marginBottom: 18 }}>
        <p className="eyebrow">Client workspace</p>
        <h1 style={{ fontSize: 34 }}>{client?.tenant.name ?? "Client"}</h1>
        <p className="lede">
          {client ? `${client.tenant.industry} · ${client.tenant.slug}` : tenantId}
        </p>
      </header>
      <ClientTabs tenantId={tenantId} />
      {children}
    </div>
  );
}
