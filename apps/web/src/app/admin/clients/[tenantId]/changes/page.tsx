import { ChangeRequestForm } from "@/components/admin/OperationsForms";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; category: string; title: string; description: string; priority: string;
  status: string; quoted_price_minor?: number | null; currency: string; created_at: string;
}> };

export default async function ChangesPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/changes/${tenantId}`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="New change request" description="Capture scope before estimating custom work">
          <ChangeRequestForm tenantId={tenantId} />
        </Panel>
        <Panel title="Revision boundary" description="Protect repository-level development time">
          <div className="notice strong">Text, image, colour, and small spacing adjustments may use included revision rounds. New sections, pages, integrations, redesigns, and custom components require a separate quote.</div>
        </Panel>
      </div>
      <Panel title="Change queue" description="Scope, quote, approval, delivery, and audit trail" flush>
        {result.items.length ? (
          <div className="table-wrap"><table><thead><tr><th>Request</th><th>Category</th><th>Priority</th><th>Status</th><th>Quote</th><th>Created</th></tr></thead><tbody>
            {result.items.map((item) => (
              <tr key={item.id}>
                <td><span className="cell-title">{item.title}</span><span className="cell-sub">{item.description}</span></td>
                <td>{item.category}</td><td><Badge>{item.priority}</Badge></td><td><Badge dark={item.status === "COMPLETED"}>{item.status}</Badge></td>
                <td>{item.quoted_price_minor == null ? "Not quoted" : `${item.currency} ${(item.quoted_price_minor / 100).toFixed(2)}`}</td>
                <td><DateText value={item.created_at} /></td>
              </tr>
            ))}
          </tbody></table></div>
        ) : <Empty title="No change requests" description="Create a structured request when the client asks for an update." />}
      </Panel>
    </div>
  );
}
