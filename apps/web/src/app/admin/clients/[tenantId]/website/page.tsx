import Link from "next/link";
import { WebsiteEditor } from "@/components/admin/WebsiteEditor";
import { Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type SiteData = {
  site: { template_key: string };
  draft: {
    id: string;
    content_snapshot: Record<string, unknown>;
    theme_snapshot: Record<string, unknown>;
    seo_snapshot: Record<string, unknown>;
  };
};

export default async function WebsitePage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const data = await serverApi<SiteData>(`/sites/tenant/${tenantId}`);
  return (
    <div className="grid sidebar-content">
      <Panel title="Theme and search metadata" description="Client-facing visual tokens and page metadata">
        <WebsiteEditor tenantId={tenantId} templateKey={data.site.template_key} draft={data.draft} mode="theme" />
      </Panel>
      <div className="stack">
        <Panel title="Draft preview" description="Authenticated and excluded from indexing">
          <p className="lede">Inspect the exact structured snapshot before it enters review.</p>
          <Link className="button" href={`/preview/${data.draft.id}`} target="_blank">Open preview</Link>
        </Panel>
        <Panel title="Design boundary" description="Controlled templates, not drag-and-drop">
          <div className="notice">
            Normal content, sections, theme tokens, and SEO metadata are managed here. Repository-level custom components stay isolated under the client override registry and are separately billable.
          </div>
        </Panel>
      </div>
    </div>
  );
}
