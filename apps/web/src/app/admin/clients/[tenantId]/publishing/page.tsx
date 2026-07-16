import Link from "next/link";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type SiteData = {
  site: { draft_version_id?: string | null; published_version_id?: string | null };
  draft: { id: string; status: string; version_number: number };
  validation: { valid: boolean; errors: string[]; warnings: string[] };
};
type Versions = { items: Array<{ id: string; version_number: number; status: string; created_at: string; published_at?: string | null }> };

export default async function PublishingPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const [data, history] = await Promise.all([
    serverApi<SiteData>(`/sites/tenant/${tenantId}`),
    serverApi<Versions>(`/sites/tenant/${tenantId}/versions`),
  ]);
  const draft = data.draft;
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title={`Version ${draft.version_number}`} description="Current controlled publication candidate">
          <div className="list">
            <div className="list-item"><div><strong>Workflow status</strong><span>Publishing is restricted to the super admin</span></div><Badge dark>{draft.status}</Badge></div>
            <div className="list-item"><div><strong>Blocking validation</strong><span>{data.validation.errors.length ? data.validation.errors.join(" · ") : "Passed"}</span></div><Badge dark={data.validation.valid}>{data.validation.valid ? "Passed" : "Failed"}</Badge></div>
            <div className="list-item"><div><strong>Advisories</strong><span>{data.validation.warnings.length ? data.validation.warnings.join(" · ") : "None"}</span></div><Badge>{data.validation.warnings.length}</Badge></div>
          </div>
          <div className="actions" style={{ marginTop: 20 }}>
            <Link className="button secondary" href={`/preview/${draft.id}`} target="_blank">Preview</Link>
            {draft.status === "DRAFT" ? <ActionButton path={`/publishing/${draft.id}/submit`} label="Submit for review" className="button" /> : null}
            {["READY_FOR_REVIEW", "CHANGES_REQUESTED"].includes(draft.status) ? <ActionButton path={`/publishing/${draft.id}/approve`} label="Approve version" className="button" /> : null}
            {draft.status === "APPROVED" ? <ActionButton path={`/publishing/${draft.id}/publish`} label="Publish website" confirm="Publish this immutable snapshot to the live website?" className="button" /> : null}
          </div>
        </Panel>
        <Panel title="Publication invariant" description="Safe production behaviour">
          <div className="notice strong">Draft changes never mutate the live website. Publishing only moves an approved immutable snapshot into the active pointer.</div>
        </Panel>
      </div>
      <Panel title="Version history" description="Every draft, approval, publication, archive, and rollback" flush>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Version</th><th>Status</th><th>Created</th><th>Published</th><th /></tr></thead>
            <tbody>
              {history.items.map((version) => (
                <tr key={version.id}>
                  <td><span className="cell-title">Version {version.version_number}</span><span className="cell-sub mono">{version.id}</span></td>
                  <td><Badge dark={version.status === "PUBLISHED"}>{version.status}</Badge></td>
                  <td><DateText value={version.created_at} /></td>
                  <td><DateText value={version.published_at} /></td>
                  <td>{["PUBLISHED", "ARCHIVED"].includes(version.status) ? <ActionButton path={`/publishing/${version.id}/rollback`} label="Restore" confirm={`Restore version ${version.version_number} as a new published snapshot?`} /> : null}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
