import Link from "next/link";
import { InvoiceForm } from "@/components/admin/OperationsForms";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; number: string; status: string; currency: string; subtotal_minor: number;
  tax_minor: number; total_minor: number; due_at?: string | null; created_at: string;
}> };

export default async function InvoicesPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/invoices/${tenantId}`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="Create invoice" description="Tax is explicit and configurable, never guessed">
          <InvoiceForm tenantId={tenantId} />
        </Panel>
        <Panel title="Commercial structure" description="Clear separation of charges">
          <div className="list">
            <div className="list-item"><div><strong>Website creation</strong><span>One-time project invoice</span></div></div>
            <div className="list-item"><div><strong>Domain</strong><span>Separate annual invoice · normally $19 for supported .com domains</span></div></div>
            <div className="list-item"><div><strong>Messaging</strong><span>Prepaid credits and receipts</span></div></div>
            <div className="list-item"><div><strong>Custom work</strong><span>Quoted and invoiced separately</span></div></div>
          </div>
        </Panel>
      </div>
      <Panel title="Invoices" description="Sequential records with issue and payment state" flush>
        {result.items.length ? (
          <div className="table-wrap"><table><thead><tr><th>Invoice</th><th>Status</th><th>Total</th><th>Due</th><th>Created</th><th /></tr></thead><tbody>
            {result.items.map((invoice) => (
              <tr key={invoice.id}>
                <td><span className="cell-title mono">{invoice.number}</span></td>
                <td><Badge dark={invoice.status === "PAID"}>{invoice.status}</Badge></td>
                <td>{invoice.currency} {(invoice.total_minor / 100).toFixed(2)}</td>
                <td><DateText value={invoice.due_at} /></td><td><DateText value={invoice.created_at} /></td>
                <td className="actions">
                  {invoice.status === "DRAFT" ? <ActionButton path={`/invoices/${tenantId}/${invoice.id}/issue`} label="Issue" /> : null}
                  {invoice.status === "ISSUED" ? <ActionButton path={`/invoices/${tenantId}/${invoice.id}/mark-paid`} label="Mark paid" confirm="Confirm that verified payment has been received?" /> : null}
                  <Link className="button secondary small" href={`/api/backend/invoices/${tenantId}/${invoice.id}/pdf`}>Download</Link>
                </td>
              </tr>
            ))}
          </tbody></table></div>
        ) : <Empty title="No invoices" description="Create the first draft invoice for this client." />}
      </Panel>
    </div>
  );
}
