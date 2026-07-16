"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["dashboard", "Overview"],
  ["leads", "Leads"],
  ["credits", "Credits"],
  ["seo", "SEO"],
  ["account", "Account"],
];

export function PortalShell({
  slug,
  clientName,
  children,
}: {
  slug: string;
  clientName: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <Link href={`/portal/${slug}/dashboard`} className="brand">
          <span className="brand-mark">Z</span>
          <span className="brand-copy"><strong>{clientName}</strong><span>Powered by Zylora</span></span>
        </Link>
        <div className="sidebar-section">Client portal</div>
        <nav className="sidebar-nav">
          {links.map(([segment, label], index) => {
            const href = `/portal/${slug}/${segment}`;
            return (
              <Link className="sidebar-link" data-active={pathname === href} href={href} key={segment}>
                <span className="sidebar-icon">{String(index + 1).padStart(2, "0")}</span><span>{label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <Link href="/api/auth/logout" className="sidebar-link"><span className="sidebar-icon">↪</span><span>Sign out</span></Link>
        </div>
      </aside>
      <section className="admin-main">
        <header className="topbar"><div className="breadcrumb"><span>Client portal</span><span>/</span><strong>{clientName}</strong></div></header>
        {children}
      </section>
    </div>
  );
}
