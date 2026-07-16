import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; visitor_id?: string | null; status: string; created_at: string; updated_at: string;
}> };

export default async function ChatbotPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/chatbot/${tenantId}/conversations`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="Grounded business assistant" description="Retrieval, citations, safe fallback, and human handoff">
          <div className="list">
            <div className="list-item"><div><strong>Knowledge isolation</strong><span>Only chunks belonging to this tenant are retrieved.</span></div><Badge dark>Enforced</Badge></div>
            <div className="list-item"><div><strong>Fallback</strong><span>Unsupported questions direct visitors to the lead form.</span></div><Badge>Safe</Badge></div>
            <div className="list-item"><div><strong>Provider mode</strong><span>Uses OpenAI when configured; otherwise deterministic grounded excerpts.</span></div><Badge>Adaptive</Badge></div>
          </div>
        </Panel>
        <Panel title="Public integration" description="Website widget API">
          <div className="notice"><span className="mono">POST /api/v1/chatbot/public</span><br />The public website passes the tenant, site, visitor ID, conversation ID, and question. Server authorization is based on the registered site and tenant configuration.</div>
        </Panel>
      </div>
      <Panel title="Conversations" description="Recent tenant-scoped visitor sessions" flush>
        {result.items.length ? (
          <div className="table-wrap"><table><thead><tr><th>Conversation</th><th>Visitor</th><th>Status</th><th>Started</th><th>Updated</th></tr></thead><tbody>
            {result.items.map((item) => <tr key={item.id}><td className="mono">{item.id}</td><td className="mono">{item.visitor_id ?? "anonymous"}</td><td><Badge>{item.status}</Badge></td><td><DateText value={item.created_at} /></td><td><DateText value={item.updated_at} /></td></tr>)}
          </tbody></table></div>
        ) : <Empty title="No chatbot conversations" description="Enable the chatbot feature and index business documents before inviting visitors to use it." />}
      </Panel>
    </div>
  );
}
