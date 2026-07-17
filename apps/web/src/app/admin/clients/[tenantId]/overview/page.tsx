import Link from "next/link";
import { PauseClientForm, TenantNoteForm } from "@/components/admin/ClientAdministration";
import { TenantProfileForm } from "@/components/admin/TenantProfileForm";
import { Badge, DateText, Metric, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Response = {
  tenant: {
    id: string; name: string; legal_name?: string | null; industry: string;
    owner_name?: string | null; email?: string | null; phone?: string | null;
    whatsapp_number?: string | null; address?: string | null;
    is_active: boolean; onboarding_complete: boolean;
    operational_status: "active" | "paused"; paused_reason?: string | null;
    paused_at?: string | null; last_login_at?: string | null;
    billing_status: "current" | "warned" | "restricted";
  };
  site?: { id: string; template_key: string; draft_version_id?: string | null; published_version_id?: string | null } | null;
  features: Record<string, boolean>;
  health: { label: string; reasons: string[]; siteStatus: string };
};
type Portal = {
  newLeads: number; totalLeads: number; messages: number; creditBalanceUsd: string;
  domain?: string | null; seoScore?: number | null; sitePublished: boolean;
};
type Note = { id: string; author_email: string; body: string; created_at: string };

export default async function OverviewPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const [data, summary, notes] = await Promise.all([
    serverApi<Response>(`/tenants/${tenantId}`),
    serverApi<Portal>(`/portal/${tenantId}/summary`).catch((): Portal => ({ newLeads: 0, totalLeads: 0, messages: 0, creditBalanceUsd: "0", domain: null, seoScore: null, sitePublished: false })),
    serverApi<{ items: Note[] }>(`/admin/clients/${tenantId}/notes`).catch(() => ({ items: [] })),
  ]);
  const paused = data.tenant.operational_status === "paused";

  return (
    <div className="stack">
      <section className="metric-grid">
        <Metric label="Total leads" value={summary.totalLeads} foot={`${summary.newLeads} new`} />
        <Metric label="WhatsApp credits" value={`$${Number(summary.creditBalanceUsd).toFixed(2)}`} foot={`${summary.messages} message jobs`} />
        <Metric label="Client health" value={data.health.label} foot={data.health.reasons.join(" · ")} />
        <Metric label="Website" value={summary.sitePublished ? "Live" : "Draft"} foot={summary.domain ?? "No primary domain"} />
      </section>
      <div className="grid sidebar-content">
        <Panel title="Client profile" description="Verified operational and contact information"><TenantProfileForm tenant={data.tenant} /></Panel>
        <div className="stack">
          <Panel title="Workspace state" description="Publishing, billing, and client activity">
            <div className="list">
              <div className="list-item"><div><strong>Operational state</strong><span>{data.tenant.paused_reason ?? "Recurring billing is active"}</span></div><Badge dark={!paused}>{paused ? "Paused" : "Active"}</Badge></div>
              <div className="list-item"><div><strong>Billing</strong><span>Independent dunning state</span></div><Badge dark={data.tenant.billing_status === "current"}>{data.tenant.billing_status}</Badge></div>
              <div className="list-item"><div><strong>Website</strong><span>{data.site?.template_key ?? "No template"} template</span></div><Badge dark={summary.sitePublished}>{summary.sitePublished ? "Published" : "Unpublished"}</Badge></div>
              <div className="list-item"><div><strong>Last client login</strong><span>Used by portfolio health filters</span></div><DateText value={data.tenant.last_login_at} /></div>
            </div>
          </Panel>
          <Panel title={paused ? "Resume client billing" : "Pause client"} description="A deliberate manual hold; this does not lock the portal or public website"><PauseClientForm tenantId={tenantId} paused={paused} /></Panel>
          <Panel title="Next actions" description="Move the client toward launch"><div className="actions"><Link className="button" href={`/admin/clients/${tenantId}/content`}>Edit content</Link><Link className="button secondary" href={`/admin/clients/${tenantId}/publishing`}>Review publishing</Link></div></Panel>
        </div>
      </div>
      <div className="grid sidebar-content">
        <Panel title="Add internal note" description="Super-admin-only, append-only client history"><TenantNoteForm tenantId={tenantId} /></Panel>
        <Panel title="Client notes" description="Previous entries are never overwritten">
          {notes.items.length ? <div className="list">{notes.items.map((note) => <article className="list-item" key={note.id}><div><strong>{note.author_email}</strong><span><DateText value={note.created_at} /></span><p style={{ whiteSpace: "pre-wrap", marginBottom: 0 }}>{note.body}</p></div></article>)}</div> : <p className="cell-sub">No internal notes have been added.</p>}
        </Panel>
      </div>
      <Panel title="Enabled modules" description="Tenant-scoped feature flags"><div className="list">{Object.entries(data.features).map(([key, enabled]) => <div className="list-item" key={key}><strong>{key.replaceAll("_", " ")}</strong><Badge dark={enabled}>{enabled ? "Enabled" : "Disabled"}</Badge></div>)}</div></Panel>
    </div>
  );
}
