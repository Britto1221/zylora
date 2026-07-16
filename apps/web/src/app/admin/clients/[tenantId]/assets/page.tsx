import Link from "next/link";
import { AssetUploadForm } from "@/components/admin/AssetUploadForm";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; filename: string; mime_type: string; size_bytes: number; category: string;
  alt_text?: string | null; status: string; created_at: string;
}> };

export default async function AssetsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/assets/${tenantId}`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="Secure asset upload" description="Tenant-prefixed object storage with signed operations">
          <AssetUploadForm tenantId={tenantId} />
        </Panel>
        <Panel title="Upload policy" description="Production safety">
          <div className="list">
            <div className="list-item"><div><strong>Allowed types</strong><span>JPEG, PNG, WebP, SVG, PDF, and plain text</span></div></div>
            <div className="list-item"><div><strong>Size limit</strong><span>Configured server-side; default 10 MB</span></div></div>
            <div className="list-item"><div><strong>Malware scanning</strong><span>Connect the documented scanning hook before accepting public uploads</span></div></div>
          </div>
        </Panel>
      </div>
      <Panel title="Asset library" description="Logos, website images, and documents" flush>
        {result.items.length ? <div className="table-wrap"><table><thead><tr><th>File</th><th>Category</th><th>Type</th><th>Size</th><th>Alt text</th><th>Status</th><th>Added</th><th /></tr></thead><tbody>
          {result.items.map((asset) => <tr key={asset.id}><td><span className="cell-title">{asset.filename}</span></td><td>{asset.category}</td><td className="mono">{asset.mime_type}</td><td>{(asset.size_bytes / 1024).toFixed(1)} KB</td><td>{asset.alt_text ?? "—"}</td><td><Badge dark={asset.status === "READY"}>{asset.status}</Badge></td><td><DateText value={asset.created_at} /></td><td className="actions"><Link className="button secondary small" href={`/api/backend/assets/${tenantId}/${asset.id}/download`}>Download</Link>{["application/pdf","text/plain"].includes(asset.mime_type) ? <ActionButton path={`/documents/${tenantId}/from-asset/${asset.id}`} label="Index" /> : null}<ActionButton path={`/assets/${tenantId}/${asset.id}`} method="DELETE" label="Delete" confirm={`Delete ${asset.filename}?`} /></td></tr>)}
        </tbody></table></div> : <Empty title="No assets" description="Upload the client logo, website images, and verified documents." />}
      </Panel>
    </div>
  );
}
