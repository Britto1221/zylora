import Link from "next/link";

export default function SecurityPage() {
  return (
    <main className="legal-page">
      <article className="legal-document">
        <Link href="/">← Back to Zylora</Link>
        <span className="settings-role">Trust centre</span>
        <h1>Security</h1>
        <p className="legal-updated">Security overview</p>
        <h2>Access control</h2>
        <p>
          Administrative settings are designed for role-based access. The included
          local preview supports separate admin and super-admin write keys, while the
          production application should connect these permissions to authenticated
          user roles.
        </p>
        <h2>Data protection</h2>
        <p>
          Production deployments should use encrypted transport, protected secrets,
          tenant-scoped authorization, verified webhooks, validated uploads, audit
          records, backups, and tested recovery procedures.
        </p>
        <h2>Responsible reporting</h2>
        <p>
          Potential security issues should be reported privately through Zylora’s
          published contact email rather than disclosed publicly.
        </p>
      </article>
    </main>
  );
}
