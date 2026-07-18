import Link from "next/link";

export default function PrivacyPage() {
  return (
    <main className="legal-page">
      <article className="legal-document">
        <Link href="/">← Back to Zylora</Link>
        <span className="settings-role">Legal</span>
        <h1>Privacy policy</h1>
        <p className="legal-updated">Last updated: 17 July 2026</p>
        <h2>Information we process</h2>
        <p>
          Zylora may process business contact information, website content, lead
          submissions, account records, and operational metadata required to provide
          the platform.
        </p>
        <h2>How information is used</h2>
        <p>
          Information is used to publish websites, deliver requested services, route
          enquiries, secure accounts, maintain billing records, and improve platform
          reliability.
        </p>
        <h2>Business ownership</h2>
        <p>
          Clients retain ownership of their business content, domains, and submitted
          lead data, subject to the applicable service agreement and legal obligations.
        </p>
        <h2>Contact</h2>
        <p>
          Privacy requests should be sent through the contact address displayed on the
          Zylora landing page.
        </p>
      </article>
    </main>
  );
}
