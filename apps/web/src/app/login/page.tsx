import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="access-page">
      <div className="access-page-grid" aria-hidden="true" />
      <section className="access-card">
        <Link className="access-brand" href="/">Zylora</Link>
        <span className="settings-role">Local access portal</span>
        <h1>Choose a workspace.</h1>
        <p>
          Choose the control centre you want to preview. Each dashboard includes direct access to its landing-page settings and public website.
        </p>

        <div className="access-options">
          <Link href="/admin/sites/demo-business/dashboard">
            <span>Admin</span>
            <strong>Open the client admin dashboard</strong>
            <small>Leads, website status, analytics, and landing details</small>
          </Link>
          <Link href="/super-admin/dashboard">
            <span>Super admin</span>
            <strong>Open the super-admin dashboard</strong>
            <small>Clients, websites, leads, operations, and Zylora details</small>
          </Link>
          <Link href="/sites/demo-business">
            <span>Public preview</span>
            <strong>Open the demo client landing page</strong>
            <small>See admin changes reflected immediately</small>
          </Link>
        </div>
      </section>
    </main>
  );
}
