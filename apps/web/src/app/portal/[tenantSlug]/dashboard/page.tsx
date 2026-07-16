import { Metric, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

export default async function ClientDashboard({
  params,
}: {
  params: Promise<{ tenantSlug: string }>;
}) {
  const { tenantSlug } = await params;
  const { tenant } = await serverApi<{ tenant: { id: string; name: string } }>(`/tenants/slug/${tenantSlug}`);
  const summary = await serverApi<{
    newLeads: number; totalLeads: number; messages: number; creditBalanceUsd: string;
    domain?: string | null; domainExpiresAt?: string | null; seoScore?: number | null; sitePublished: boolean;
  }>(`/portal/${tenant.id}/summary`);
  return (
    <main className="page">
      <PageHeader eyebrow="Client intelligence" title="Overview" description="Leads, messaging, domain, and organic-search performance in one place." />
      <section className="metric-grid">
        <Metric label="New leads" value={summary.newLeads} foot={`${summary.totalLeads} total`} />
        <Metric label="Credit balance" value={`$${Number(summary.creditBalanceUsd).toFixed(2)}`} foot="Prepaid WhatsApp services" />
        <Metric label="SEO score" value={summary.seoScore ?? "—"} foot="Latest completed audit" />
        <Metric label="Website" value={summary.sitePublished ? "Live" : "Offline"} foot={summary.domain ?? "No primary domain"} />
      </section>
      <div className="grid two">
        <Panel title="Operational promise" description="Credits affect messaging only">
          <div className="notice strong">Your website, contact form, lead records, dashboard, and exports remain available even when messaging credits reach zero.</div>
        </Panel>
        <Panel title="Domain" description="Renewal is separate from messaging credits">
          <div className="list">
            <div className="list-item"><strong className="mono">{summary.domain ?? "Not connected"}</strong></div>
            <div className="list-item"><div><strong>Expiry</strong><span>{summary.domainExpiresAt ? new Date(summary.domainExpiresAt).toLocaleDateString() : "Not recorded"}</span></div></div>
          </div>
        </Panel>
      </div>
    </main>
  );
}
