import Link from "next/link";
import {
  DashboardArrow,
  DashboardCheck,
  DashboardShell,
  type DashboardNavigationItem,
} from "@/components/dashboard/dashboard-shell";
import { getPlatformSettings, getTenantSiteSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

const navigation: DashboardNavigationItem[] = [
  { label: "Overview", href: "/super-admin/dashboard", icon: "overview", active: true },
  { label: "Clients", href: "#clients", icon: "clients", badge: "3" },
  { label: "Websites", href: "#websites", icon: "website" },
  { label: "Leads", href: "#activity", icon: "leads", badge: "18" },
  { label: "Billing", href: "#operations", icon: "billing" },
  { label: "Domains", href: "#operations", icon: "domains" },
  { label: "Zylora details", href: "/super-admin/settings", icon: "settings" },
];

const clients = [
  {
    slug: "demo-business",
    industry: "Professional services",
    leads: 48,
    status: "Live",
  },
  {
    slug: "northstar-clinic",
    industry: "Clinic & wellness",
    leads: 31,
    status: "Review",
  },
  {
    slug: "vertex-academy",
    industry: "School & coaching",
    leads: 69,
    status: "Live",
  },
];

function titleFromSlug(slug: string) {
  return slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export default async function SuperAdminDashboardPage() {
  const [platformSettings, demoSettings] = await Promise.all([
    getPlatformSettings(),
    getTenantSiteSettings("demo-business"),
  ]);

  return (
    <DashboardShell
      roleLabel="Super admin"
      workspaceName="Zylora"
      workspaceSubtitle="Platform control centre"
      userName="Britto K"
      userInitials="BK"
      navigation={navigation}
    >
      <section className="dashboard-page-heading">
        <div>
          <span className="dashboard-page-eyebrow">Platform overview</span>
          <h1>Good evening, Britto.</h1>
          <p>
            Monitor every client workspace, public website, lead flow, and platform
            setting from one operating view.
          </p>
        </div>
        <div className="dashboard-heading-actions">
          <Link className="dashboard-secondary-action" href="/sites/demo-business">
            Open demo website
          </Link>
          <Link className="dashboard-primary-action" href="/super-admin/settings">
            Change Zylora details
            <DashboardArrow />
          </Link>
        </div>
      </section>

      <section className="dashboard-metric-grid" aria-label="Platform metrics">
        <article className="dashboard-metric-card">
          <div>
            <span>Client workspaces</span>
            <em>+2 this month</em>
          </div>
          <strong>24</strong>
          <div className="dashboard-mini-bars" aria-hidden="true">
            <i style={{ height: "36%" }} />
            <i style={{ height: "48%" }} />
            <i style={{ height: "42%" }} />
            <i style={{ height: "62%" }} />
            <i style={{ height: "76%" }} />
            <i style={{ height: "92%" }} />
          </div>
        </article>
        <article className="dashboard-metric-card">
          <div>
            <span>Published websites</span>
            <em>95.8% active</em>
          </div>
          <strong>23</strong>
          <div className="dashboard-progress-line"><i style={{ width: "95.8%" }} /></div>
        </article>
        <article className="dashboard-metric-card">
          <div>
            <span>Leads this month</span>
            <em>+18.4%</em>
          </div>
          <strong>1,284</strong>
          <div className="dashboard-metric-note">148 captured in the last 7 days</div>
        </article>
        <article className="dashboard-metric-card">
          <div>
            <span>Platform revenue</span>
            <em>+12.7%</em>
          </div>
          <strong>₹1.86L</strong>
          <div className="dashboard-metric-note">One-time builds, changes, and credits</div>
        </article>
      </section>

      <section className="dashboard-two-column" id="clients">
        <article className="dashboard-panel dashboard-panel-large">
          <div className="dashboard-panel-heading">
            <div>
              <span>Client portfolio</span>
              <h2>Active workspaces</h2>
            </div>
            <Link href="/admin/sites/demo-business/dashboard">
              Open client dashboard <DashboardArrow />
            </Link>
          </div>

          <div className="dashboard-client-table">
            <div className="dashboard-table-header">
              <span>Client</span>
              <span>Status</span>
              <span>Leads</span>
              <span>Action</span>
            </div>
            {clients.map((client, index) => {
              const name = index === 0 ? demoSettings.businessName : titleFromSlug(client.slug);
              return (
                <div className="dashboard-table-row" key={client.slug}>
                  <div className="dashboard-client-identity">
                    <span>{name.slice(0, 2).toUpperCase()}</span>
                    <div>
                      <strong>{name}</strong>
                      <small>{client.industry}</small>
                    </div>
                  </div>
                  <span className={`dashboard-status dashboard-status-${client.status.toLowerCase()}`}>
                    <i /> {client.status}
                  </span>
                  <strong className="dashboard-table-value">{client.leads}</strong>
                  {index === 0 ? (
                    <Link className="dashboard-row-action" href={`/admin/sites/${client.slug}/dashboard`}>
                      Manage
                    </Link>
                  ) : (
                    <span className="dashboard-row-action muted">Preview</span>
                  )}
                </div>
              );
            })}
          </div>
        </article>

        <article className="dashboard-panel dashboard-contact-panel">
          <div className="dashboard-panel-heading">
            <div>
              <span>Public identity</span>
              <h2>Zylora contact</h2>
            </div>
          </div>
          <div className="dashboard-contact-orb">Z</div>
          <span className="dashboard-contact-label">Landing-page email</span>
          <strong className="dashboard-contact-value">{platformSettings.zyloraContactEmail}</strong>
          <small>
            Updated {new Date(platformSettings.updatedAt).toLocaleDateString("en-IN", {
              day: "numeric",
              month: "short",
              year: "numeric",
            })}
          </small>
          <Link className="dashboard-settings-action" href="/super-admin/settings">
            Change Zylora landing details
            <DashboardArrow />
          </Link>
        </article>
      </section>

      <section className="dashboard-three-column" id="operations">
        <article className="dashboard-panel">
          <div className="dashboard-panel-heading compact">
            <div>
              <span>Operations</span>
              <h2>Platform health</h2>
            </div>
          </div>
          <div className="dashboard-health-list">
            <div><span><DashboardCheck /> Public websites</span><strong>23 / 24</strong></div>
            <div><span><DashboardCheck /> Lead delivery</span><strong>Operational</strong></div>
            <div><span><DashboardCheck /> Settings storage</span><strong>Connected</strong></div>
            <div><span><DashboardCheck /> Domain checks</span><strong>1 pending</strong></div>
          </div>
        </article>

        <article className="dashboard-panel" id="websites">
          <div className="dashboard-panel-heading compact">
            <div>
              <span>Publishing</span>
              <h2>Website pipeline</h2>
            </div>
          </div>
          <div className="dashboard-pipeline">
            <div><span>Published</span><strong>23</strong><i><b style={{ width: "88%" }} /></i></div>
            <div><span>In review</span><strong>3</strong><i><b style={{ width: "42%" }} /></i></div>
            <div><span>Draft</span><strong>5</strong><i><b style={{ width: "55%" }} /></i></div>
          </div>
        </article>

        <article className="dashboard-panel" id="activity">
          <div className="dashboard-panel-heading compact">
            <div>
              <span>Activity</span>
              <h2>Recent events</h2>
            </div>
          </div>
          <div className="dashboard-activity-feed">
            <div><i /><p><strong>Landing details updated</strong><span>{demoSettings.businessName} · 12 min ago</span></p></div>
            <div><i /><p><strong>New lead captured</strong><span>Vertex Academy · 28 min ago</span></p></div>
            <div><i /><p><strong>Website published</strong><span>Northstar Clinic · 1 hr ago</span></p></div>
          </div>
        </article>
      </section>
    </DashboardShell>
  );
}
