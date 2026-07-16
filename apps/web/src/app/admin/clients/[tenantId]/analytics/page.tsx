import { Metric, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Data = {
  periodDays: number; events: Record<string, number>; pageViews: number;
  leads: number; conversionRate: number; topPages: Array<{ path: string; views: number }>;
};

export default async function AnalyticsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const data = await serverApi<Data>(`/analytics/${tenantId}?days=30`);
  return (
    <div className="stack">
      <section className="metric-grid">
        <Metric label="Page views" value={data.pageViews} foot="Last 30 days" />
        <Metric label="Leads" value={data.leads} foot="Stored submissions" />
        <Metric label="Conversion rate" value={`${data.conversionRate}%`} foot="Lead submissions / page views" />
        <Metric label="Tracked events" value={Object.values(data.events).reduce((sum, value) => sum + value, 0)} foot="First-party operational events" />
      </section>
      <div className="grid two">
        <Panel title="Event distribution" description="Privacy-conscious first-party events">
          <div className="list">
            {Object.entries(data.events).length ? Object.entries(data.events).map(([key, value]) => (
              <div className="list-item" key={key}><strong>{key.replaceAll("_", " ")}</strong><span>{value}</span></div>
            )) : <div className="notice">No analytics events have been received.</div>}
          </div>
        </Panel>
        <Panel title="Top pages" description="Most viewed routes">
          <div className="list">
            {data.topPages.length ? data.topPages.map((page) => (
              <div className="list-item" key={page.path}><strong className="mono">{page.path}</strong><span>{page.views} views</span></div>
            )) : <div className="notice">No page-view data yet.</div>}
          </div>
        </Panel>
      </div>
    </div>
  );
}
