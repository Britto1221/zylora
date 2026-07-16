import Link from "next/link";
import { Badge, Empty, PageHeader, Panel, DateText } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Tenant = {
  id: string; name: string; slug: string; industry: string; owner_name?: string | null;
  email?: string | null; is_active: boolean; onboarding_complete: boolean; created_at: string;
};
type Result = { items: Tenant[]; total: number };

export default async function ClientsPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string }>;
}) {
  const query = await searchParams;
  let result: Result = { items: [], total: 0 };
  try {
    result = await serverApi<Result>(`/tenants?search=${encodeURIComponent(query.search ?? "")}`);
  } catch {}
  return (
    <main className="page">
      <PageHeader
        eyebrow="Client portfolio"
        title="Clients"
        description={`${result.total} managed workspace${result.total === 1 ? "" : "s"}, each isolated by tenant.`}
        actions={<Link className="button" href="/admin/clients/new">New client</Link>}
      />
      <Panel title="Managed businesses" description="Search, open, and operate every client from one view" flush
        action={
          <form>
            <input className="input" name="search" defaultValue={query.search ?? ""} placeholder="Search clients…" style={{ width: 220 }} />
          </form>
        }
      >
        {result.items.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Client</th><th>Industry</th><th>Owner</th><th>Status</th><th>Created</th><th /></tr></thead>
              <tbody>
                {result.items.map((client) => (
                  <tr key={client.id}>
                    <td>
                      <Link className="cell-title" href={`/admin/clients/${client.id}/overview`}>{client.name}</Link>
                      <span className="cell-sub mono">{client.slug}</span>
                    </td>
                    <td>{client.industry}</td>
                    <td><span className="cell-title">{client.owner_name ?? "Not assigned"}</span><span className="cell-sub">{client.email ?? ""}</span></td>
                    <td><Badge dark={client.is_active}>{client.is_active ? "Active" : "Inactive"}</Badge></td>
                    <td><DateText value={client.created_at} /></td>
                    <td><Link className="button secondary small" href={`/admin/clients/${client.id}/overview`}>Open</Link></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Empty title="No matching clients" description="Create a client workspace to begin onboarding and website production." actionHref="/admin/clients/new" actionLabel="Create client" />}
      </Panel>
    </main>
  );
}
