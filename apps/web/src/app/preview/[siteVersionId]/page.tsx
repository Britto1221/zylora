export default async function PreviewPage({
  params,
}: {
  params: Promise<{ siteVersionId: string }>;
}) {
  const { siteVersionId } = await params;

  return (
    <main>
      <p className="muted">Preview version {siteVersionId}</p>
      <h1>Authenticated website preview</h1>
      <section className="card">
        Connect this route to the authenticated API endpoint:
        <code> /sites/preview/{siteVersionId}</code>
      </section>
    </main>
  );
}
