import Link from "next/link";
import {
  DashboardArrow,
  DashboardCheck,
  DashboardShell,
  type DashboardNavigationItem,
} from "@/components/dashboard/dashboard-shell";
import { getTenantSiteSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

const recentLeads = [
  { name: "Ananya Sharma", type: "Consultation request", source: "Homepage", status: "New", time: "8 min ago" },
  { name: "Rahul Menon", type: "Service enquiry", source: "Organic search", status: "Qualified", time: "42 min ago" },
  { name: "Priya Nair", type: "Callback request", source: "Contact page", status: "Contacted", time: "2 hrs ago" },
  { name: "Arjun Thomas", type: "Pricing enquiry", source: "Service page", status: "New", time: "4 hrs ago" },
];

export default async function AdminDashboardPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const settings = await getTenantSiteSettings(slug);

  const navigation: DashboardNavigationItem[] = [
    { label: "Overview", href: `/admin/sites/${slug}/dashboard`, icon: "overview", active: true },
    { label: "Public website", href: `/sites/${slug}`, icon: "website" },
    { label: "Leads", href: "#leads", icon: "leads", badge: "4" },
    { label: "Analytics", href: "#analytics", icon: "billing" },
    { label: "Domain", href: "#website-health", icon: "domains" },
    { label: "Landing details", href: `/admin/sites/${slug}/settings`, icon: "settings" },
  ];

  return (
    <DashboardShell
      roleLabel="Client admin"
      workspaceName={settings.businessName}
      workspaceSubtitle={`sites/${slug}`}
      userName="Workspace Admin"
      userInitials="WA"
      navigation={navigation}
    >
      <section className="dashboard-page-heading">
        <div>
          <span className="dashboard-page-eyebrow">Client workspace</span>
          <h1>{settings.businessName}</h1>
          <p>
            Track the public website, incoming leads, contact details, and business
            performance from one focused workspace.
          </p>
        </div>
        <div className="dashboard-heading-actions">
          <Link className="dashboard-secondary-action" href={`/sites/${slug}`}>
            View public website
          </Link>
          <Link className="dashboard-primary-action" href={`/admin/sites/${slug}/settings`}>
            Change landing details
            <DashboardArrow />
          </Link>
        </div>
      </section>

      <section className="dashboard-metric-grid" id="analytics" aria-label="Client metrics">
        <article className="dashboard-metric-card">
          <div><span>New leads</span><em>+18.4%</em></div>
          <strong>148</strong>
          <div className="dashboard-mini-bars" aria-hidden="true">
            <i style={{ height: "32%" }} />
            <i style={{ height: "51%" }} />
            <i style={{ height: "43%" }} />
            <i style={{ height: "67%" }} />
            <i style={{ height: "79%" }} />
            <i style={{ height: "94%" }} />
          </div>
        </article>
        <article className="dashboard-metric-card">
          <div><span>Website visits</span><em>+26.7%</em></div>
          <strong>4,921</strong>
          <div className="dashboard-metric-note">1,203 visitors from organic search</div>
        </article>
        <article className="dashboard-metric-card">
          <div><span>Lead conversion</span><em>+2.1%</em></div>
          <strong>12.8%</strong>
          <div className="dashboard-progress-line"><i style={{ width: "72%" }} /></div>
        </article>
        <article className="dashboard-metric-card">
          <div><span>Contact completeness</span><em>Ready</em></div>
          <strong>100%</strong>
          <div className="dashboard-progress-line"><i style={{ width: "100%" }} /></div>
        </article>
      </section>

      <section className="dashboard-two-column" id="leads">
        <article className="dashboard-panel dashboard-panel-large">
          <div className="dashboard-panel-heading">
            <div>
              <span>Lead operations</span>
              <h2>Recent enquiries</h2>
            </div>
            <span className="dashboard-panel-meta">Last updated now</span>
          </div>
          <div className="dashboard-lead-list">
            {recentLeads.map((lead) => (
              <div className="dashboard-lead-row" key={`${lead.name}-${lead.time}`}>
                <span className="dashboard-lead-avatar">
                  {lead.name.split(" ").map((part) => part[0]).slice(0, 2).join("")}
                </span>
                <div className="dashboard-lead-main">
                  <strong>{lead.name}</strong>
                  <small>{lead.type} · {lead.source}</small>
                </div>
                <span className={`dashboard-lead-status dashboard-lead-${lead.status.toLowerCase()}`}>
                  {lead.status}
                </span>
                <time>{lead.time}</time>
              </div>
            ))}
          </div>
        </article>

        <article className="dashboard-panel dashboard-contact-panel">
          <div className="dashboard-panel-heading">
            <div>
              <span>Landing-page details</span>
              <h2>Public contact</h2>
            </div>
          </div>
          <div className="dashboard-detail-list">
            <div><span>Email</span><strong>{settings.email}</strong></div>
            <div><span>Phone</span><strong>{settings.phone}</strong></div>
            <div><span>Address</span><strong>{settings.address}</strong></div>
          </div>
          <Link className="dashboard-settings-action" href={`/admin/sites/${slug}/settings`}>
            Edit email, phone, and address
            <DashboardArrow />
          </Link>
        </article>
      </section>

      <section className="dashboard-three-column" id="website-health">
        <article className="dashboard-panel">
          <div className="dashboard-panel-heading compact">
            <div><span>Website</span><h2>Publishing status</h2></div>
          </div>
          <div className="dashboard-publish-status">
            <span><i /> Live</span>
            <strong>Published successfully</strong>
            <small>Public route: /sites/{slug}</small>
          </div>
          <Link className="dashboard-inline-link" href={`/sites/${slug}`}>
            Open live site <DashboardArrow />
          </Link>
        </article>

        <article className="dashboard-panel">
          <div className="dashboard-panel-heading compact">
            <div><span>Business profile</span><h2>Setup checklist</h2></div>
          </div>
          <div className="dashboard-health-list">
            <div><span><DashboardCheck /> Business name</span><strong>Complete</strong></div>
            <div><span><DashboardCheck /> Public email</span><strong>Complete</strong></div>
            <div><span><DashboardCheck /> Phone number</span><strong>Complete</strong></div>
            <div><span><DashboardCheck /> Address</span><strong>Complete</strong></div>
          </div>
        </article>

        <article className="dashboard-panel">
          <div className="dashboard-panel-heading compact">
            <div><span>Performance</span><h2>Traffic sources</h2></div>
          </div>
          <div className="dashboard-pipeline">
            <div><span>Organic search</span><strong>48%</strong><i><b style={{ width: "48%" }} /></i></div>
            <div><span>Direct</span><strong>31%</strong><i><b style={{ width: "31%" }} /></i></div>
            <div><span>Social</span><strong>21%</strong><i><b style={{ width: "21%" }} /></i></div>
          </div>
        </article>
      </section>
    </DashboardShell>
  );
}
