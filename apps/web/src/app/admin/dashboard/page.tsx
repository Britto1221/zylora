import Link from "next/link";
import { Metric, PageHeader, Panel, Badge, Empty, DateText } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Summary = {
  metrics: Record<string, number>;
  recentLeads: Array<{
    id: string; tenantId: string; name: string; service?: string | null;
    status: string; createdAt: string;
  }>;
  expiringDomains: Array<{
    id: string; tenantId: string; hostname: string; status: string; expiresAt?: string | null;
  }>;
};

export default async function AdminDashboard() {
  let data: Summary = { metrics: {}, recentLeads: [], expiringDomains: [] };
  let unavailable = false;
  try {
    data = await serverApi<Summary>("/dashboard/summary");
  } catch {
    unavailable = true;
  }
  const metrics = data.metrics;
  return (
    <main className="page">
      <PageHeader
        eyebrow="Portfolio intelligence"
        title="Control centre"
        description="A single monochromatic command surface for every website, lead, domain, credit balance, and growth workflow."
        actions={<Link className="button" href="/admin/clients/new">Add client</Link>}
      />
      {unavailable ? <div className="notice strong" style={{ marginBottom: 18 }}>The API is unavailable. Start FastAPI on port 8000 to load live operations data.</div> : null}
      <section className="metric-grid">
        <Metric label="Active clients" value={metrics.activeClients ?? 0} foot={`${metrics.clients ?? 0} total workspaces`} />
        <Metric label="Published websites" value={metrics.publishedSites ?? 0} foot={`${metrics.draftSites ?? 0} drafts in progress`} />
        <Metric label="New leads · 24h" value={metrics.newLeads ?? 0} foot="Stored before notifications" />
        <Metric label="Credit alerts" value={metrics.creditAlerts ?? 0} foot={`${metrics.failedMessages ?? 0} failed messages`} />
      </section>
      <div className="grid two">
        <Panel title="Recent leads" description="Latest opportunities across all clients" flush>
          {data.recentLeads.length ? (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Lead</th><th>Service</th><th>Status</th><th>Received</th></tr></thead>
                <tbody>
                  {data.recentLeads.map((lead) => (
                    <tr key={lead.id}>
                      <td><Link className="cell-title" href={`/admin/clients/${lead.tenantId}/leads`}>{lead.name}</Link></td>
                      <td>{lead.service ?? "General enquiry"}</td>
                      <td><Badge dark={lead.status === "NEW"}>{lead.status}</Badge></td>
                      <td><DateText value={lead.createdAt} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <Empty title="No leads yet" description="Published website submissions will appear here automatically." />}
        </Panel>
        <Panel title="Domain attention" description="Upcoming renewal and verification work" flush>
          {data.expiringDomains.length ? (
            <div className="table-wrap">
              <table>
                <thead><tr><th>Domain</th><th>Status</th><th>Expiry</th></tr></thead>
                <tbody>
                  {data.expiringDomains.map((domain) => (
                    <tr key={domain.id}>
                      <td><Link className="cell-title mono" href={`/admin/clients/${domain.tenantId}/domains`}>{domain.hostname}</Link></td>
                      <td><Badge>{domain.status}</Badge></td>
                      <td><DateText value={domain.expiresAt} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <Empty title="No renewal pressure" description="Verified domains and their renewal dates will be tracked here." />}
        </Panel>
      </div>
    </main>
  );
}
