export default async function ClientDashboard({
  params,
}: {
  params: Promise<{ tenantSlug: string }>;
}) {
  const { tenantSlug } = await params;

  return (
    <main>
      <p className="muted">{tenantSlug}</p>
      <h1>Client Dashboard</h1>
      <div className="grid grid-3">
        <section className="card">New leads</section>
        <section className="card">WhatsApp credits</section>
        <section className="card">Domain renewal</section>
        <section className="card">SEO score</section>
      </div>
    </main>
  );
}
