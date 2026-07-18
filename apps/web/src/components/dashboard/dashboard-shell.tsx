import Link from "next/link";
import type { ReactNode } from "react";

type DashboardIconName =
  | "overview"
  | "clients"
  | "website"
  | "leads"
  | "billing"
  | "domains"
  | "settings"
  | "external";

export type DashboardNavigationItem = {
  label: string;
  href: string;
  icon: DashboardIconName;
  active?: boolean;
  badge?: string;
};

type DashboardShellProps = {
  roleLabel: string;
  workspaceName: string;
  workspaceSubtitle: string;
  userName: string;
  userInitials: string;
  navigation: DashboardNavigationItem[];
  children: ReactNode;
};

function BrandMark() {
  return (
    <span className="brand-mark dashboard-brand-mark" aria-hidden="true">
      <span />
      <span />
      <span />
    </span>
  );
}

function DashboardIcon({ name }: { name: DashboardIconName }) {
  const common = {
    viewBox: "0 0 24 24",
    "aria-hidden": true,
  } as const;

  if (name === "overview") {
    return (
      <svg {...common}>
        <rect x="3" y="3" width="7" height="7" rx="2" />
        <rect x="14" y="3" width="7" height="7" rx="2" />
        <rect x="3" y="14" width="7" height="7" rx="2" />
        <rect x="14" y="14" width="7" height="7" rx="2" />
      </svg>
    );
  }

  if (name === "clients") {
    return (
      <svg {...common}>
        <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" />
      </svg>
    );
  }

  if (name === "website") {
    return (
      <svg {...common}>
        <circle cx="12" cy="12" r="9" />
        <path d="M3 12h18M12 3c3 3.3 3 14.7 0 18M12 3c-3 3.3-3 14.7 0 18" />
      </svg>
    );
  }

  if (name === "leads") {
    return (
      <svg {...common}>
        <path d="M5 5h14v11H9l-4 4V5Z" />
        <path d="M8 9h8M8 12h5" />
      </svg>
    );
  }

  if (name === "billing") {
    return (
      <svg {...common}>
        <rect x="3" y="5" width="18" height="14" rx="3" />
        <path d="M3 10h18M7 15h3" />
      </svg>
    );
  }

  if (name === "domains") {
    return (
      <svg {...common}>
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
      </svg>
    );
  }

  if (name === "settings") {
    return (
      <svg {...common}>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21H9.6v-.1A1.7 1.7 0 0 0 8.5 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H3V9.6h.1A1.7 1.7 0 0 0 4.6 8.5a1.7 1.7 0 0 0-.34-1.88l-.06-.06 2.83-2.83.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1V3h4v.1A1.7 1.7 0 0 0 15.5 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06 2.83 2.83-.06.06A1.7 1.7 0 0 0 19.4 9c.18.37.42.7.75.94.32.24.7.38 1.1.4H21v4h-.1A1.7 1.7 0 0 0 19.4 15Z" />
      </svg>
    );
  }

  return (
    <svg {...common}>
      <path d="M14 3h7v7M10 14 21 3M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5" />
    </svg>
  );
}

export function DashboardShell({
  roleLabel,
  workspaceName,
  workspaceSubtitle,
  userName,
  userInitials,
  navigation,
  children,
}: DashboardShellProps) {
  return (
    <div className="dashboard-app-shell">
      <aside className="dashboard-app-sidebar">
        <div className="dashboard-app-brand-row">
          <Link className="dashboard-app-brand" href="/">
            <BrandMark />
            <span>Zylora</span>
          </Link>
          <span className="dashboard-role-chip">{roleLabel}</span>
        </div>

        <div className="dashboard-workspace-card">
          <span className="dashboard-workspace-monogram">
            {workspaceName.slice(0, 2).toUpperCase()}
          </span>
          <div>
            <strong>{workspaceName}</strong>
            <small>{workspaceSubtitle}</small>
          </div>
        </div>

        <nav className="dashboard-app-nav" aria-label={`${roleLabel} navigation`}>
          {navigation.map((item) => (
            <Link
              className={item.active ? "dashboard-nav-item active" : "dashboard-nav-item"}
              href={item.href}
              key={`${item.label}-${item.href}`}
            >
              <span className="dashboard-nav-icon">
                <DashboardIcon name={item.icon} />
              </span>
              <span>{item.label}</span>
              {item.badge ? <em>{item.badge}</em> : null}
            </Link>
          ))}
        </nav>

        <div className="dashboard-sidebar-support">
          <span>Workspace status</span>
          <strong>
            <i /> All systems operational
          </strong>
          <small>Settings and public pages are connected.</small>
        </div>

        <div className="dashboard-sidebar-user">
          <span>{userInitials}</span>
          <div>
            <strong>{userName}</strong>
            <small>{roleLabel}</small>
          </div>
          <Link href="/login" aria-label="Change workspace">
            <DashboardIcon name="external" />
          </Link>
        </div>
      </aside>

      <div className="dashboard-app-main">
        <header className="dashboard-app-topbar">
          <div className="dashboard-mobile-brand">
            <BrandMark />
            <span>Zylora</span>
          </div>
          <label className="dashboard-search-control">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>
            <input aria-label="Search dashboard" placeholder="Search workspace" />
            <kbd>⌘ K</kbd>
          </label>
          <div className="dashboard-topbar-actions">
            <Link href="/" className="dashboard-topbar-link">
              View Zylora
            </Link>
            <button className="dashboard-icon-button" type="button" aria-label="Notifications">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M14 21h-4" />
              </svg>
              <i />
            </button>
            <span className="dashboard-topbar-avatar">{userInitials}</span>
          </div>
        </header>

        <main className="dashboard-app-content">{children}</main>
      </div>
    </div>
  );
}

export function DashboardArrow() {
  return (
    <svg className="dashboard-arrow" viewBox="0 0 20 20" aria-hidden="true">
      <path d="M4 10h11M11 5l5 5-5 5" />
    </svg>
  );
}

export function DashboardCheck() {
  return (
    <svg className="dashboard-check" viewBox="0 0 20 20" aria-hidden="true">
      <path d="m4 10 3.3 3.3L16 5.8" />
    </svg>
  );
}
