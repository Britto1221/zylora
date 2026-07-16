import { DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; actor_user_id: string; action: string; entity_type: string;
  entity_id?: string | null; payload: Record<string, unknown>; created_at: string;
}> };

export default async function AuditPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/audit/${tenantId}`);
  return (
    <Panel title="Immutable activity trail" description="Sensitive client, publishing, billing, and access actions" flush>
      {result.items.length ? (
        <div className="table-wrap"><table><thead><tr><th>Action</th><th>Entity</th><th>Actor</th><th>Details</th><th>Date</th></tr></thead><tbody>
          {result.items.map((item) => (
            <tr key={item.id}>
              <td><span className="cell-title">{item.action}</span></td>
              <td><span>{item.entity_type}</span><span className="cell-sub mono">{item.entity_id ?? "—"}</span></td>
              <td className="mono">{item.actor_user_id}</td>
              <td><span className="cell-sub mono">{JSON.stringify(item.payload)}</span></td>
              <td><DateText value={item.created_at} /></td>
            </tr>
          ))}
        </tbody></table></div>
      ) : <Empty title="No audit activity" description="Client and production changes will be recorded here." />}
    </Panel>
  );
}
