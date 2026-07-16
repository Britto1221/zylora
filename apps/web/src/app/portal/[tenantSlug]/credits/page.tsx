import { DateText, Empty, Metric, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

export default async function PortalCredits({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const { tenantSlug } = await params;
  const { tenant } = await serverApi<{ tenant: { id: string } }>(`/tenants/slug/${tenantSlug}`);
  const data = await serverApi<{ account: { balanceUsd: string; reservedUsd: string; availableUsd: string }; transactions: Array<{ id: string; type: string; description: string; amount_micro_usd: number; balance_after_micro_usd: number; created_at: string }> }>(`/credits/${tenant.id}`);
  return (
    <main className="page">
      <PageHeader eyebrow="Prepaid services" title="Credits" description="Transparent USD usage for chargeable WhatsApp notifications." />
      <section className="metric-grid">
        <Metric label="Balance" value={`$${Number(data.account.balanceUsd).toFixed(2)}`} />
        <Metric label="Reserved" value={`$${Number(data.account.reservedUsd).toFixed(4)}`} />
        <Metric label="Available" value={`$${Number(data.account.availableUsd).toFixed(2)}`} />
        <Metric label="Website availability" value="Always on" foot="Independent of credits" />
      </section>
      <Panel title="Transaction history" description="Append-only service credit records" flush>
        {data.transactions.length ? <div className="table-wrap"><table><thead><tr><th>Type</th><th>Description</th><th>Amount</th><th>Balance</th><th>Date</th></tr></thead><tbody>
          {data.transactions.map((item) => <tr key={item.id}><td>{item.type}</td><td>{item.description}</td><td>${(item.amount_micro_usd / 1_000_000).toFixed(6)}</td><td>${(item.balance_after_micro_usd / 1_000_000).toFixed(6)}</td><td><DateText value={item.created_at} /></td></tr>)}
        </tbody></table></div> : <Empty title="No transactions" description="Your verified top-ups and messaging usage will appear here." />}
      </Panel>
    </main>
  );
}
