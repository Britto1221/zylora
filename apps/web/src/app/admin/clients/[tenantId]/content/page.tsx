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
  validation: { valid: boolean; errors: string[]; warnings: string[] };
};

export default async function ContentPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const data = await serverApi<SiteData>(`/sites/tenant/${tenantId}`);
  return (
    <div className="grid sidebar-content">
      <Panel title="Website content" description="Constrained fields plus structured advanced editing">
        <WebsiteEditor tenantId={tenantId} templateKey={data.site.template_key} draft={data.draft} mode="content" />
      </Panel>
      <Panel title="Draft validation" description="Checks run every time the draft is saved">
        {data.validation.valid ? <div className="success">The current draft passes blocking validation.</div> : <div className="error">{data.validation.errors.length} blocking issue(s) must be fixed.</div>}
        <div className="list" style={{ marginTop: 16 }}>
          {data.validation.errors.map((item) => <div className="list-item" key={item}><div><strong>Blocking</strong><span>{item}</span></div></div>)}
          {data.validation.warnings.map((item) => <div className="list-item" key={item}><div><strong>Advisory</strong><span>{item}</span></div></div>)}
          {!data.validation.errors.length && !data.validation.warnings.length ? <div className="notice">No current validation findings.</div> : null}
        </div>
      </Panel>
    </div>
  );
}
