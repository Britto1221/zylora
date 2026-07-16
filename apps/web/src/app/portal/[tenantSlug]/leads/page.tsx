import { Badge, DateText, Empty, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

export default async function PortalLeads({
  params,
}: {
  params: Promise<{ tenantSlug: string }>;
}) {
  const { tenantSlug } = await params;
  const { tenant } = await serverApi<{ tenant: { id: string } }>(`/tenants/slug/${tenantSlug}`);
  const result = await serverApi<{ items: Array<{
    id: string; name: string; email?: string | null; phone?: string | null;
    service?: string | null; status: string; created_at: string;
  }>; total: number }>(`/leads/tenant/${tenant.id}`);
  return (
    <main className="page">
      <PageHeader eyebrow="Customer enquiries" title="Leads" description={`${result.total} captured opportunities`} />
      <Panel title="Lead records" description="Contact details remain available regardless of messaging balance" flush>
        {result.items.length ? <div className="table-wrap"><table><thead><tr><th>Lead</th><th>Service</th><th>Contact</th><th>Status</th><th>Received</th></tr></thead><tbody>
          {result.items.map((lead) => <tr key={lead.id}><td><strong>{lead.name}</strong></td><td>{lead.service ?? "General enquiry"}</td><td><span className="cell-title">{lead.phone ?? ""}</span><span className="cell-sub">{lead.email ?? ""}</span></td><td><Badge>{lead.status}</Badge></td><td><DateText value={lead.created_at} /></td></tr>)}
        </tbody></table></div> : <Empty title="No leads yet" description="New website enquiries will appear here." />}
      </Panel>
    </main>
  );
}
