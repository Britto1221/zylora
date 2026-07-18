import Link from "next/link";
import { TenantSiteSettingsForm } from "@/components/admin/tenant-site-settings-form";
import { getTenantSiteSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

export default async function AdminSiteSettingsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const settings = await getTenantSiteSettings(slug);

  return (
    <main className="settings-page-shell">
      <div className="settings-page-grid" aria-hidden="true" />
      <section className="settings-panel">
        <div className="settings-panel-header">
          <div>
            <span className="settings-role">Admin / Landing page</span>
            <h1>Contact details</h1>
            <p>
              Update the email address, phone number, and physical address shown on
              this client’s public landing page.
            </p>
          </div>
          <Link className="settings-back-link" href={`/admin/sites/${slug}/dashboard`}>
            Back to dashboard
          </Link>
        </div>

        <div className="settings-context-card">
          <span>Editing site</span>
          <strong>{settings.businessName}</strong>
          <code>/sites/{slug}</code>
        </div>

        <TenantSiteSettingsForm slug={slug} initialSettings={settings} />
      </section>
    </main>
  );
}
