import Link from "next/link";

export default function TermsPage() {
  return (
    <main className="legal-page">
      <article className="legal-document">
        <Link href="/">← Back to Zylora</Link>
        <span className="settings-role">Legal</span>
        <h1>Terms of service</h1>
        <p className="legal-updated">Last updated: 17 July 2026</p>
        <h2>Platform services</h2>
        <p>
          Zylora provides managed website, publishing, lead, communication, AI, domain,
          and related digital-business services according to the selected engagement.
        </p>
        <h2>Client responsibilities</h2>
        <p>
          Clients are responsible for the accuracy and legality of supplied content,
          maintaining required approvals, and responding to renewal or payment notices.
        </p>
        <h2>Usage and availability</h2>
        <p>
          Paid messaging, AI, or third-party services may depend on available credits,
          provider availability, and external platform policies. Public websites and
          stored leads should not be disabled solely because messaging credits expire.
        </p>
        <h2>Changes</h2>
        <p>
          Custom changes, integrations, and ongoing growth services may be quoted and
          billed separately from the initial website delivery.
        </p>
      </article>
    </main>
  );
}
