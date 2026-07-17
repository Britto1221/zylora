import Link from "next/link";
import {
  BillingSettingsForm,
  ClientExportButton,
  InvoiceForm,
} from "@/components/admin/OperationsForms";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Invoice = {
  id: string;
  number: string;
  status: string;
  invoice_type: "ONE_TIME" | "RECURRING";
  billing_period?: string | null;
  auto_generated: boolean;
  currency: string;
  subtotal_minor: number;
  tax_minor: number;
  total_minor: number;
  due_at?: string | null;
  created_at: string;
};

type BillingConfiguration = {
  monthlyAmountMinor: number;
  billingCurrency: "USD" | "INR";
  billingDay: number;
  billingStatus: "current" | "warned" | "restricted";
};

export default async function InvoicesPage({
  params,
}: {
  params: Promise<{ tenantId: string }>;
}) {
  const { tenantId } = await params;
  const [result, configuration] = await Promise.all([
    serverApi<{ items: Invoice[] }>(`/invoices/${tenantId}`),
    serverApi<BillingConfiguration>(`/billing/${tenantId}/configuration`),
  ]);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel
          title="Recurring monthly billing"
          description="Configured independently per client in USD or INR"
        >
          <BillingSettingsForm tenantId={tenantId} configuration={configuration} />
        </Panel>
        <Panel
          title="Standalone handoff"
          description="Export only this client's static website and public assets"
        >
          <ClientExportButton tenantId={tenantId} />
        </Panel>
      </div>

      <div className="grid sidebar-content">
        <Panel
          title="Create one-time invoice"
          description="Upfront setup fees and custom work remain separate from recurring billing"
        >
          <InvoiceForm tenantId={tenantId} />
        </Panel>
        <Panel title="Commercial structure" description="Charges remain operationally separate">
          <div className="list">
            <div className="list-item"><div><strong>Website creation</strong><span>One-time project invoice</span></div></div>
            <div className="list-item"><div><strong>Monthly service</strong><span>Automatically generated from this client’s billing configuration</span></div></div>
            <div className="list-item"><div><strong>Domain</strong><span>Separate annual invoice · normally $19 for supported .com domains</span></div></div>
            <div className="list-item"><div><strong>Messaging</strong><span>Prepaid credits and receipts</span></div></div>
            <div className="list-item"><div><strong>Custom work</strong><span>Quoted and invoiced separately</span></div></div>
          </div>
        </Panel>
      </div>

      <Panel title="Invoices" description="One-time and recurring records remain distinct" flush>
        {result.items.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Invoice</th><th>Type</th><th>Status</th><th>Total</th><th>Due</th><th>Created</th><th /></tr></thead>
              <tbody>
                {result.items.map((invoice) => (
                  <tr key={invoice.id}>
                    <td><span className="cell-title mono">{invoice.number}</span><span className="cell-sub">{invoice.billing_period ?? "One-time"}</span></td>
                    <td><Badge>{invoice.invoice_type === "RECURRING" ? "Recurring" : "One-time"}</Badge></td>
                    <td><Badge dark={invoice.status === "PAID"}>{invoice.status}</Badge></td>
                    <td>{invoice.currency} {(invoice.total_minor / 100).toFixed(2)}</td>
                    <td><DateText value={invoice.due_at} /></td>
                    <td><DateText value={invoice.created_at} /></td>
                    <td className="actions">
                      {invoice.status === "DRAFT" ? <ActionButton path={`/invoices/${tenantId}/${invoice.id}/issue`} label="Issue" /> : null}
                      {["ISSUED", "OVERDUE"].includes(invoice.status) ? <ActionButton path={`/invoices/${tenantId}/${invoice.id}/mark-paid`} label="Mark paid" confirm="Confirm that verified payment has been received?" /> : null}
                      <Link className="button secondary small" href={`/api/backend/invoices/${tenantId}/${invoice.id}/pdf`}>Download</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Empty title="No invoices" description="Create the first one-time invoice or configure monthly billing." />}
      </Panel>
    </div>
  );
}
