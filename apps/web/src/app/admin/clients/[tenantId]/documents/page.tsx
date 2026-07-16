import { TextDocumentForm } from "@/components/admin/OperationsForms";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: Array<{
  id: string; name: string; category: string; mime_type: string; status: string;
  error_message?: string | null; created_at: string;
}> };

export default async function DocumentsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const result = await serverApi<Result>(`/documents/${tenantId}`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="Add verified knowledge" description="Paste business content for extraction and RAG indexing">
          <TextDocumentForm tenantId={tenantId} />
        </Panel>
        <Panel title="Storage boundary" description="Local development and production">
          <div className="notice">
            Text ingestion is fully operational locally. Production file uploads use the documented S3-compatible signed-upload boundary and require storage credentials plus malware scanning.
          </div>
        </Panel>
      </div>
      <Panel title="Knowledge documents" description="Tenant-isolated extraction and chatbot index" flush>
        {result.items.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Document</th><th>Category</th><th>Type</th><th>Status</th><th>Added</th><th /></tr></thead>
              <tbody>
                {result.items.map((document) => (
                  <tr key={document.id}>
                    <td><span className="cell-title">{document.name}</span>{document.error_message ? <span className="cell-sub">{document.error_message}</span> : null}</td>
                    <td>{document.category}</td>
                    <td className="mono">{document.mime_type}</td>
                    <td><Badge dark={document.status === "READY"}>{document.status}</Badge></td>
                    <td><DateText value={document.created_at} /></td>
                    <td><ActionButton path={`/documents/${tenantId}/${document.id}`} method="DELETE" label="Delete" confirm={`Delete ${document.name} and its indexed chunks?`} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Empty title="No documents indexed" description="Add verified content to power tenant-specific chatbot answers." />}
      </Panel>
    </div>
  );
}
