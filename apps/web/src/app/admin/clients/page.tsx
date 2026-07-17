import Link from "next/link";
import { ClientBulkTable, type ClientListItem } from "@/components/admin/ClientBulkTable";
import { Empty, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Result = { items: ClientListItem[]; total: number };
type Query = {
  search?: string;
  billingStatus?: string;
  siteStatus?: string;
  lastLoginFrom?: string;
  lastLoginTo?: string;
  lastLoginMissing?: string;
};

export default async function ClientsPage({ searchParams }: { searchParams: Promise<Query> }) {
  const query = await searchParams;
  const params = new URLSearchParams();
  if (query.search) params.set("search", query.search);
  if (query.billingStatus) params.set("billing_status", query.billingStatus);
  if (query.siteStatus) params.set("site_status", query.siteStatus);
  if (query.lastLoginFrom) params.set("last_login_from", new Date(`${query.lastLoginFrom}T00:00:00Z`).toISOString());
  if (query.lastLoginTo) params.set("last_login_to", new Date(`${query.lastLoginTo}T23:59:59Z`).toISOString());
  if (query.lastLoginMissing === "true") params.set("last_login_missing", "true");
  params.set("page_size", "100");

  let result: Result = { items: [], total: 0 };
  try {
    result = await serverApi<Result>(`/tenants?${params.toString()}`);
  } catch {}

  return (
    <main className="page">
      <PageHeader
        eyebrow="Client portfolio"
        title="Clients"
        description={`${result.total} matching workspace${result.total === 1 ? "" : "s"}, with billing, publishing, and activity health in one view.`}
        actions={<Link className="button" href="/admin/clients/new">New client</Link>}
      />
      <Panel title="Filters" description="Filter before selecting clients for an audited bulk operation">
        <form className="field-grid" method="get">
          <div className="field"><label htmlFor="search">Search</label><input className="input" id="search" name="search" defaultValue={query.search ?? ""} placeholder="Name, slug, or email" /></div>
          <div className="field"><label htmlFor="billingStatus">Billing status</label><select className="select" id="billingStatus" name="billingStatus" defaultValue={query.billingStatus ?? ""}><option value="">Any</option><option value="current">Current</option><option value="warned">Warned</option><option value="restricted">Restricted</option></select></div>
          <div className="field"><label htmlFor="siteStatus">Site status</label><select className="select" id="siteStatus" name="siteStatus" defaultValue={query.siteStatus ?? ""}><option value="">Any</option><option value="live">Live</option><option value="draft">Draft</option></select></div>
          <div className="field"><label htmlFor="lastLoginFrom">Last login from</label><input className="input" id="lastLoginFrom" name="lastLoginFrom" type="date" defaultValue={query.lastLoginFrom ?? ""} /></div>
          <div className="field"><label htmlFor="lastLoginTo">Last login to</label><input className="input" id="lastLoginTo" name="lastLoginTo" type="date" defaultValue={query.lastLoginTo ?? ""} /></div>
          <div className="field"><label htmlFor="lastLoginMissing">Login record</label><select className="select" id="lastLoginMissing" name="lastLoginMissing" defaultValue={query.lastLoginMissing ?? ""}><option value="">Any</option><option value="true">Never logged in</option></select></div>
          <div className="actions"><button className="button" type="submit">Apply filters</button><Link className="button secondary" href="/admin/clients">Clear</Link></div>
        </form>
      </Panel>
      <Panel title="Managed businesses" description="Health labels always display the underlying reasons" flush>
        {result.items.length ? <ClientBulkTable clients={result.items} /> : <Empty title="No matching clients" description="Change the filters or create a client workspace." actionHref="/admin/clients/new" actionLabel="Create client" />}
      </Panel>
    </main>
  );
}
