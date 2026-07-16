export default async function Page({
  params,
}: {
  params: Promise<{ tenantId: string }>;
}) {
  const { tenantId } = await params;

  return (
    <main>
      <p className="muted">Client {tenantId}</p>
      <h1>Leads</h1>
      <section className="card">
        Production module boundary for leads.
      </section>
    </main>
  );
}
