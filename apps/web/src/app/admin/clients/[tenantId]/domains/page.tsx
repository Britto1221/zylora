import { DomainForm } from "@/components/admin/OperationsForms";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; hostname: string; domain_type: string; status: string; is_primary: boolean;
  registered_to_client: boolean; expires_at?: string | null; renewal_price_usd: string;
  verification_token?: string | null;
}> };

export default async function DomainsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/domains/${tenantId}`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="Connect a domain" description="Custom domains and managed Zylora subdomains">
          <DomainForm tenantId={tenantId} />
        </Panel>
        <Panel title="Renewal liability" description="Contractual boundary">
          <div className="notice strong">Zylora sends reminders at 60, 30, 15, and 7 days. After the final reminder, non-renewal is the client’s responsibility under the service agreement.</div>
        </Panel>
      </div>
      <Panel title="Domain registry" description="Verification, ownership, primary routing, and renewal state" flush>
        {result.items.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Hostname</th><th>Type</th><th>Status</th><th>Ownership</th><th>Renewal</th><th>Expiry</th><th /></tr></thead>
              <tbody>
                {result.items.map((domain) => (
                  <tr key={domain.id}>
                    <td><span className="cell-title mono">{domain.hostname}</span><span className="cell-sub">{domain.is_primary ? "Primary domain" : "Alternate domain"}</span></td>
                    <td>{domain.domain_type}</td>
                    <td><Badge dark={domain.status === "ACTIVE"}>{domain.status}</Badge></td>
                    <td>{domain.registered_to_client ? "Client legal name" : "Needs review"}</td>
                    <td>${Number(domain.renewal_price_usd).toFixed(2)} / year</td>
                    <td><DateText value={domain.expires_at} /></td>
                    <td className="actions">
                      {domain.status !== "ACTIVE" ? <ActionButton path={`/domains/${tenantId}/${domain.id}/verify?confirmed=true`} label="Confirm DNS" /> : null}
                      <ActionButton path={`/domains/${tenantId}/${domain.id}`} method="DELETE" label="Remove" confirm={`Remove ${domain.hostname}?`} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Empty title="No domains connected" description="Add the client’s domain or a Zylora subdomain to configure routing." />}
      </Panel>
    </div>
  );
}
