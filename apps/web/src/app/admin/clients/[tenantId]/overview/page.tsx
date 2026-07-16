import Link from "next/link";
import { TenantProfileForm } from "@/components/admin/TenantProfileForm";
import { Badge, Metric, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Response = {
  tenant: {
    id: string; name: string; legal_name?: string | null; industry: string;
    owner_name?: string | null; email?: string | null; phone?: string | null;
    whatsapp_number?: string | null; address?: string | null;
    is_active: boolean; onboarding_complete: boolean;
  };
  site?: { id: string; template_key: string; draft_version_id?: string | null; published_version_id?: string | null } | null;
  features: Record<string, boolean>;
};
type Portal = {
  newLeads: number; totalLeads: number; messages: number; creditBalanceUsd: string;
  domain?: string | null; seoScore?: number | null; sitePublished: boolean;
};

export default async function OverviewPage({
  params,
}: {
  params: Promise<{ tenantId: string }>;
}) {
  const { tenantId } = await params;
  const [data, summary] = await Promise.all([
    serverApi<Response>(`/tenants/${tenantId}`),
    serverApi<Portal>(`/portal/${tenantId}/summary`).catch((): Portal => ({
      newLeads: 0,
      totalLeads: 0,
      messages: 0,
      creditBalanceUsd: "0",
      domain: null,
      seoScore: null,
      sitePublished: false,
    })),
  ]);

  return (
    <div className="stack">
      <section className="metric-grid">
        <Metric label="Total leads" value={summary.totalLeads} foot={`${summary.newLeads} new`} />
        <Metric label="WhatsApp credits" value={`$${Number(summary.creditBalanceUsd).toFixed(2)}`} foot={`${summary.messages} message jobs`} />
        <Metric label="SEO score" value={summary.seoScore ?? "—"} foot="Latest completed audit" />
        <Metric label="Website" value={summary.sitePublished ? "Live" : "Draft"} foot={summary.domain ?? "No primary domain"} />
      </section>
      <div className="grid sidebar-content">
        <Panel title="Client profile" description="Verified operational and contact information">
          <TenantProfileForm tenant={data.tenant} />
        </Panel>
        <div className="stack">
          <Panel title="Workspace state" description="Publishing and onboarding">
            <div className="list">
              <div className="list-item"><div><strong>Onboarding</strong><span>Client information and business intake</span></div><Badge dark={data.tenant.onboarding_complete}>{data.tenant.onboarding_complete ? "Complete" : "In progress"}</Badge></div>
              <div className="list-item"><div><strong>Website</strong><span>{data.site?.template_key ?? "No template"} template</span></div><Badge dark={summary.sitePublished}>{summary.sitePublished ? "Published" : "Unpublished"}</Badge></div>
              <div className="list-item"><div><strong>Primary domain</strong><span className="mono">{summary.domain ?? "Not connected"}</span></div></div>
            </div>
          </Panel>
          <Panel title="Enabled modules" description="Tenant-scoped feature flags">
            <div className="list">
              {Object.entries(data.features).map(([key, enabled]) => (
                <div className="list-item" key={key}>
                  <strong>{key.replaceAll("_", " ")}</strong><Badge dark={enabled}>{enabled ? "Enabled" : "Disabled"}</Badge>
                </div>
              ))}
            </div>
          </Panel>
          <Panel title="Next actions" description="Move the client toward launch">
            <div className="actions">
              <Link className="button" href={`/admin/clients/${tenantId}/content`}>Edit content</Link>
              <Link className="button secondary" href={`/admin/clients/${tenantId}/publishing`}>Review publishing</Link>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
