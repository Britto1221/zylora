import { Badge, Empty, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

export default async function PortalSeo({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const { tenantSlug } = await params;
  const { tenant } = await serverApi<{ tenant: { id: string } }>(`/tenants/slug/${tenantSlug}`);
  const result = await serverApi<{ items: Array<{ id: string; score?: number | null; grade?: string | null; summary?: string | null; recommendations_json: Array<Record<string, string>>; status: string }> }>(`/seo/${tenant.id}`);
  const latest = result.items[0];
  return (
    <main className="page">
      <PageHeader eyebrow="Organic visibility" title="SEO" description="Approved findings and recommended improvements." />
      {latest ? <div className="grid sidebar-content"><Panel title="Current audit" description={latest.summary ?? ""}><div style={{ fontSize: 80, fontWeight: 750, letterSpacing: "-.08em" }}>{latest.score ?? "—"}</div><Badge dark>Grade {latest.grade ?? "—"}</Badge></Panel><Panel title="Recommendations" description="Changes are reviewed before they reach the live website"><div className="list">{latest.recommendations_json.map((item, index) => <div className="list-item" key={index}><div><strong>{item.title}</strong><span>{item.recommendation}</span></div></div>)}</div></Panel></div> : <Panel title="SEO report" description="No completed audit"><Empty title="No SEO baseline" description="Your Zylora administrator will run and review the first audit." /></Panel>}
    </main>
  );
}
