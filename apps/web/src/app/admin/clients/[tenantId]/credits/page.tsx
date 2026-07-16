import { CreditTopUpForm } from "@/components/admin/OperationsForms";
import { Badge, DateText, Empty, Metric, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Data = {
  account: {
    balanceUsd: string; reservedUsd: string; availableUsd: string;
    low_balance_threshold_micro_usd: number; currency: string;
  };
  transactions: Array<{
    id: string; type: string; amount_micro_usd: number; balance_after_micro_usd: number;
    description: string; external_reference?: string | null; created_at: string;
  }>;
};

export default async function CreditsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const data = await serverApi<Data>(`/credits/${tenantId}`);
  return (
    <div className="stack">
      <section className="metric-grid">
        <Metric label="Current balance" value={`$${Number(data.account.balanceUsd).toFixed(2)}`} foot="Universal USD service credits" />
        <Metric label="Reserved" value={`$${Number(data.account.reservedUsd).toFixed(4)}`} foot="Pending provider operations" />
        <Metric label="Available" value={`$${Number(data.account.availableUsd).toFixed(2)}`} foot="Safe to spend" />
        <Metric label="Low-balance threshold" value={`$${(data.account.low_balance_threshold_micro_usd / 1_000_000).toFixed(2)}`} foot="Dashboard and email warning" />
      </section>
      <div className="grid sidebar-content">
        <Panel title="Manual verified top-up" description="Use until automated checkout volume justifies full payment automation">
          <CreditTopUpForm tenantId={tenantId} />
        </Panel>
        <Panel title="Credit rules" description="Non-cash, non-transferable service balance">
          <div className="list">
            <div className="list-item"><div><strong>Integer accounting</strong><span>All values use micro-USD, never floating point.</span></div></div>
            <div className="list-item"><div><strong>Atomic charging</strong><span>Reservations and deductions use row locking and idempotency.</span></div></div>
            <div className="list-item"><div><strong>Separate renewals</strong><span>Domain funds never enter the messaging credit account.</span></div></div>
          </div>
        </Panel>
      </div>
      <Panel title="Append-only transaction history" description="Corrections are new adjustments; previous records are never edited" flush>
        {data.transactions.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Type</th><th>Description</th><th>Amount</th><th>Balance after</th><th>Reference</th><th>Date</th></tr></thead>
              <tbody>
                {data.transactions.map((item) => (
                  <tr key={item.id}>
                    <td><Badge dark={item.amount_micro_usd > 0}>{item.type}</Badge></td>
                    <td>{item.description}</td>
                    <td>{item.amount_micro_usd > 0 ? "+" : ""}${(item.amount_micro_usd / 1_000_000).toFixed(6)}</td>
                    <td>${(item.balance_after_micro_usd / 1_000_000).toFixed(6)}</td>
                    <td className="mono">{item.external_reference ?? "—"}</td>
                    <td><DateText value={item.created_at} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Empty title="No transactions" description="Verified purchases, deductions, refunds, and adjustments will appear here." />}
      </Panel>
    </div>
  );
}
