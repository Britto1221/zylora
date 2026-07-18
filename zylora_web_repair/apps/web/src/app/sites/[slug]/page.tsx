import Link from "next/link";
import { getTenantSiteSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

function ContactIcon({ type }: { type: "email" | "phone" | "address" }) {
  if (type === "email") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m4 7 8 6 8-6" />
      </svg>
    );
  }
  if (type === "phone") {
    return (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M7 3h3l1.2 4-2 1.6a15 15 0 0 0 6.2 6.2l1.6-2 4 1.2v3c0 2.2-1.8 4-4 4C9.3 21 3 14.7 3 7c0-2.2 1.8-4 4-4Z" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z" />
      <circle cx="12" cy="10" r="2.5" />
    </svg>
  );
}

export default async function TenantLandingPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const settings = await getTenantSiteSettings(slug);
  const telephoneHref = settings.phone.replace(/[^+\d]/g, "");

  return (
    <div className="tenant-landing-page">
      <header className="tenant-header">
        <div className="tenant-container tenant-header-inner">
          <Link className="tenant-brand" href={`/sites/${slug}`}>
            <span>{settings.businessName.slice(0, 1).toUpperCase()}</span>
            {settings.businessName}
          </Link>
          <a className="button button-dark button-small" href="#contact">
            Contact us
          </a>
        </div>
      </header>

      <main>
        <section className="tenant-hero">
          <div className="tenant-grid-overlay" aria-hidden="true" />
          <div className="tenant-container tenant-hero-layout">
            <div>
              <span className="tenant-eyebrow">A Zylora-powered business</span>
              <h1>Clear services. Trusted information. Easier conversations.</h1>
              <p>
                {settings.businessName} now has one focused place where customers can
                understand the business and reach the right team without friction.
              </p>
              <div className="tenant-hero-actions">
                <a className="button button-primary" href={`mailto:${settings.email}`}>
                  Send an email
                </a>
                <a className="button button-secondary" href={`tel:${telephoneHref}`}>
                  Call now
                </a>
              </div>
            </div>
            <aside className="tenant-feature-panel">
              <span>Business contact</span>
              <strong>Everything customers need, in one place.</strong>
              <p>
                These details are managed from the Zylora admin settings page and are
                updated without changing source code.
              </p>
            </aside>
          </div>
        </section>

        <section className="tenant-contact-section" id="contact">
          <div className="tenant-container">
            <span className="section-index">Contact</span>
            <div className="tenant-contact-heading">
              <h2>Start a conversation.</h2>
              <p>Choose the most convenient way to reach {settings.businessName}.</p>
            </div>

            <div className="tenant-contact-grid">
              <a href={`mailto:${settings.email}`}>
                <span className="tenant-contact-icon"><ContactIcon type="email" /></span>
                <small>Email</small>
                <strong>{settings.email}</strong>
              </a>
              <a href={`tel:${telephoneHref}`}>
                <span className="tenant-contact-icon"><ContactIcon type="phone" /></span>
                <small>Phone</small>
                <strong>{settings.phone}</strong>
              </a>
              <article>
                <span className="tenant-contact-icon"><ContactIcon type="address" /></span>
                <small>Address</small>
                <strong>{settings.address}</strong>
              </article>
            </div>
          </div>
        </section>
      </main>

      <footer className="tenant-footer">
        <div className="tenant-container tenant-footer-inner">
          <span>© {new Date().getFullYear()} {settings.businessName}</span>
          <span>Powered by Zylora</span>
        </div>
      </footer>
    </div>
  );
}
