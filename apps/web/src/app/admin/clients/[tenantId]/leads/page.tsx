import Link from "next/link";
import { LeadStatus } from "@/components/admin/LeadActions";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = {
  items: Array<{
    id: string; name: string; email?: string | null; phone?: string | null;
    service?: string | null; status: string; source: string; whatsapp_consent: boolean; created_at: string;
  }>;
  total: number;
};

export default async function LeadsPage({
  params,
  searchParams,
}: {
  params: Promise<{ tenantId: string }>;
  searchParams: Promise<{ search?: string; status?: string }>;
}) {
  const { tenantId } = await params;
  const query = await searchParams;
  const result = await serverApi<Result>(
    `/leads/tenant/${tenantId}?search=${encodeURIComponent(query.search ?? "")}&status=${encodeURIComponent(query.status ?? "")}`,
  );
  return (
    <Panel title="Lead pipeline" description={`${result.total} stored lead${result.total === 1 ? "" : "s"}`} flush
      action={
        <div className="actions">
          <form className="actions">
            <input className="input" name="search" defaultValue={query.search ?? ""} placeholder="Search lead…" style={{ width: 180 }} />
            <select className="select" name="status" defaultValue={query.status ?? ""} style={{ width: 130 }}><option value="">All statuses</option>{["NEW","CONTACTED","QUALIFIED","FOLLOW_UP","CONVERTED","LOST","SPAM"].map((status) => <option key={status}>{status}</option>)}</select>
            <button className="button secondary small">Filter</button>
          </form>
          <Link className="button secondary small" href={`/api/backend/leads/tenant/${tenantId}/export/csv`}>Export CSV</Link>
        </div>
      }
    >
      {result.items.length ? (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Lead</th><th>Service</th><th>Contact</th><th>Consent</th><th>Status</th><th>Received</th></tr></thead>
            <tbody>
              {result.items.map((lead) => (
                <tr key={lead.id}>
                  <td><span className="cell-title">{lead.name}</span><span className="cell-sub">{lead.source}</span></td>
                  <td>{lead.service ?? "General enquiry"}</td>
                  <td><span className="cell-title">{lead.phone ?? "No phone"}</span><span className="cell-sub">{lead.email ?? ""}</span></td>
                  <td><Badge dark={lead.whatsapp_consent}>{lead.whatsapp_consent ? "WhatsApp yes" : "No consent"}</Badge></td>
                  <td><LeadStatus tenantId={tenantId} leadId={lead.id} value={lead.status} /></td>
                  <td><DateText value={lead.created_at} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : <Empty title="No leads found" description="The website continues storing leads even when messaging credits are unavailable." />}
    </Panel>
  );
}
