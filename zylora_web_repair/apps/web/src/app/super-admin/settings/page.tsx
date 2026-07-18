import Link from "next/link";
import { PlatformSettingsForm } from "@/components/admin/platform-settings-form";
import { getPlatformSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

export default async function SuperAdminSettingsPage() {
  const settings = await getPlatformSettings();

  return (
    <main className="settings-page-shell">
      <div className="settings-page-grid" aria-hidden="true" />
      <section className="settings-panel">
        <div className="settings-panel-header">
          <div>
            <span className="settings-role">Super admin / Zylora</span>
            <h1>Platform contact email</h1>
            <p>
              Control the email shown on Zylora’s own landing page without editing the
              frontend source code.
            </p>
          </div>
          <Link className="settings-back-link" href="/super-admin/dashboard">
            Back to dashboard
          </Link>
        </div>

        <div className="settings-context-card">
          <span>Current public email</span>
          <strong>{settings.zyloraContactEmail}</strong>
          <code>Last updated {new Date(settings.updatedAt).toLocaleString("en-IN")}</code>
        </div>

        <PlatformSettingsForm initialSettings={settings} />
      </section>
    </main>
  );
}
