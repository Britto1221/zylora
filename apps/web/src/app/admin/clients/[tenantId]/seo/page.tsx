export default async function Page({
  params,
}: {
  params: Promise<{ tenantId: string }>;
}) {
  const { tenantId } = await params;

  return (
    <main>
      <p className="muted">Client {tenantId}</p>
      <h1>Seo</h1>
      <section className="card">
        Production module boundary for seo.
      </section>
    </main>
  );
}
