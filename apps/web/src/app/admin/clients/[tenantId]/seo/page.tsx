import Link from "next/link";
import { SeoRunButton } from "@/components/admin/OperationsForms";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; status: string; score?: number | null; grade?: string | null;
  summary?: string | null; issues_json: Array<Record<string, string>>;
  recommendations_json: Array<Record<string, string>>; created_at: string;
}> };

export default async function SeoPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/seo/${tenantId}`);
  const latest = result.items[0];
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="Organic search audit" description="Rule-based snapshot analysis with controlled draft fixes">
          <p className="lede">Audit the active draft or published snapshot. Findings never modify production automatically.</p>
          <div className="actions" style={{ marginTop: 18 }}><SeoRunButton tenantId={tenantId} /></div>
        </Panel>
        <Panel title="Latest score" description={latest?.summary ?? "Run the first audit"}>
          {latest ? (
            <div>
              <div style={{ fontSize: 64, fontWeight: 750, letterSpacing: "-.07em" }}>{latest.score ?? "—"}</div>
              <Badge dark={latest.grade === "A"}>Grade {latest.grade ?? "—"}</Badge><div className="actions" style={{ marginTop: 16 }}><Link className="button secondary small" href={`/api/backend/seo/${tenantId}/${latest.id}/pdf`}>Download PDF</Link></div>
            </div>
          ) : <div className="empty"><div><strong>No SEO history</strong><p>Run an audit to establish the baseline.</p></div></div>}
        </Panel>
      </div>
      {latest ? (
        <div className="grid two">
          <Panel title="Issues" description={`${latest.issues_json.length} finding(s)`}>
            <div className="list">
              {latest.issues_json.length ? latest.issues_json.map((item, index) => (
                <div className="list-item" key={`${item.code}-${index}`}>
                  <div><strong>{item.title}</strong><span>{item.detail}</span></div><Badge>{item.severity}</Badge>
                </div>
              )) : <div className="notice">No current issues.</div>}
            </div>
          </Panel>
          <Panel title="Recommendations" description="Apply through the draft workflow">
            <div className="list">
              {latest.recommendations_json.length ? latest.recommendations_json.map((item, index) => (
                <div className="list-item" key={`${item.code}-${index}`}>
                  <div><strong>{item.title}</strong><span>{item.recommendation}</span></div>
                </div>
              )) : <div className="notice">No recommendations are pending.</div>}
            </div>
          </Panel>
        </div>
      ) : null}
      <Panel title="Audit history" description="Scores are tied to immutable version IDs" flush>
        {result.items.length ? (
          <div className="table-wrap"><table><thead><tr><th>Date</th><th>Status</th><th>Score</th><th>Grade</th><th>Summary</th></tr></thead><tbody>
            {result.items.map((audit) => <tr key={audit.id}><td><DateText value={audit.created_at} /></td><td><Badge>{audit.status}</Badge></td><td>{audit.score ?? "—"}</td><td>{audit.grade ?? "—"}</td><td>{audit.summary ?? ""}</td></tr>)}
          </tbody></table></div>
        ) : <Empty title="No audits" description="SEO audits will appear here after they run." />}
      </Panel>
    </div>
  );
}
