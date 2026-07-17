import Link from "next/link";
import { Badge, DateText, Empty, Metric, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type CurrencyTotals = { count?: number; USD: number; INR: number };
type InvoiceItem = {
  invoiceId: string;
  tenantId: string;
  client: string;
  number: string;
  currency: "USD" | "INR";
  amountMinor: number;
  dueAt: string;
};
type Revenue = {
  mrr: { USD: number; INR: number };
  billableClients: number;
  upcoming7Days: CurrencyTotals;
  upcoming30Days: CurrencyTotals;
  overdue: CurrencyTotals;
  billingStatusCounts: { current: number; warned: number; restricted: number };
  upcomingItems: InvoiceItem[];
  overdueItems: InvoiceItem[];
  generatedAt: string;
};

function money(currency: string, minor: number) {
  return `${currency} ${(minor / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default async function RevenuePage() {
  const data = await serverApi<Revenue>("/dashboard/revenue");
  return (
    <main className="page">
      <PageHeader eyebrow="Commercial operations" title="Revenue" description={`Aggregated from tenant billing configuration and invoices. Refreshed ${new Date(data.generatedAt).toLocaleString()}.`} />
      <section className="metric-grid">
        <Metric label="MRR · USD" value={money("USD", data.mrr.USD)} foot={`${data.billableClients} active billable clients across currencies`} />
        <Metric label="MRR · INR" value={money("INR", data.mrr.INR)} foot="Currencies remain separate; no forced conversion" />
        <Metric label="Overdue · USD" value={money("USD", data.overdue.USD)} foot={`${data.overdue.count ?? 0} overdue recurring invoices`} />
        <Metric label="Overdue · INR" value={money("INR", data.overdue.INR)} foot="Verified unpaid recurring invoices" />
      </section>
      <div className="grid sidebar-content">
        <Panel title="Upcoming recurring renewals" description="Issued recurring invoices due in the next 7 and 30 days">
          <div className="list">
            <div className="list-item"><div><strong>Next 7 days</strong><span>{data.upcoming7Days.count ?? 0} invoices</span></div><div className="cell-sub">{money("USD", data.upcoming7Days.USD)} · {money("INR", data.upcoming7Days.INR)}</div></div>
            <div className="list-item"><div><strong>Next 30 days</strong><span>{data.upcoming30Days.count ?? 0} invoices</span></div><div className="cell-sub">{money("USD", data.upcoming30Days.USD)} · {money("INR", data.upcoming30Days.INR)}</div></div>
          </div>
        </Panel>
        <Panel title="Clients by billing status" description="Current dunning state stored on each tenant">
          <div className="list">
            <div className="list-item"><strong>Current</strong><Badge dark>{data.billingStatusCounts.current}</Badge></div>
            <div className="list-item"><strong>Warned</strong><Badge>{data.billingStatusCounts.warned}</Badge></div>
            <div className="list-item"><strong>Restricted</strong><Badge>{data.billingStatusCounts.restricted}</Badge></div>
          </div>
        </Panel>
      </div>
      <Panel title="Upcoming invoices" description="Recurring invoice due dates" flush>
        {data.upcomingItems.length ? <div className="table-wrap"><table><thead><tr><th>Client</th><th>Invoice</th><th>Amount</th><th>Due</th><th /></tr></thead><tbody>{data.upcomingItems.map((item) => <tr key={item.invoiceId}><td><Link className="cell-title" href={`/admin/clients/${item.tenantId}/invoices`}>{item.client}</Link></td><td className="mono">{item.number}</td><td>{money(item.currency, item.amountMinor)}</td><td><DateText value={item.dueAt} /></td><td><Link className="button secondary small" href={`/admin/clients/${item.tenantId}/invoices`}>Open</Link></td></tr>)}</tbody></table></div> : <Empty title="No upcoming renewals" description="No recurring invoices are due within the next 30 days." />}
      </Panel>
      <Panel title="Overdue recurring invoices" description="Amounts remain separated by invoice currency" flush>
        {data.overdueItems.length ? <div className="table-wrap"><table><thead><tr><th>Client</th><th>Invoice</th><th>Amount</th><th>Due</th><th /></tr></thead><tbody>{data.overdueItems.map((item) => <tr key={item.invoiceId}><td><Link className="cell-title" href={`/admin/clients/${item.tenantId}/invoices`}>{item.client}</Link></td><td className="mono">{item.number}</td><td>{money(item.currency, item.amountMinor)}</td><td><DateText value={item.dueAt} /></td><td><Link className="button secondary small" href={`/admin/clients/${item.tenantId}/invoices`}>Resolve</Link></td></tr>)}</tbody></table></div> : <Empty title="Nothing overdue" description="All recurring invoices are current." />}
      </Panel>
    </main>
  );
}
