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
  billingStatus,
  daysPastDue,
  children,
}: {
  slug: string;
  clientName: string;
  billingStatus: "current" | "warned" | "restricted";
  daysPastDue: number;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const restricted = billingStatus === "restricted";
  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <Link href={restricted ? `/portal/${slug}/pay-now` : `/portal/${slug}/dashboard`} className="brand">
          <span className="brand-mark">Z</span>
          <span className="brand-copy"><strong>{clientName}</strong><span>Powered by Zylora</span></span>
        </Link>
        <div className="sidebar-section">Client portal</div>
        <nav className="sidebar-nav">
          {restricted ? (
            <Link className="sidebar-link" data-active href={`/portal/${slug}/pay-now`}>
              <span className="sidebar-icon">01</span><span>Pay now</span>
            </Link>
          ) : links.map(([segment, label], index) => {
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
        {billingStatus === "warned" ? (
          <div className="billing-banner" role="alert">
            <strong>Payment overdue.</strong>
            <span>Your recurring invoice is {daysPastDue} days overdue. Full access remains available until day 10.</span>
            <Link href={`/portal/${slug}/pay-now`}>Pay now</Link>
          </div>
        ) : null}
        {children}
      </section>
    </div>
  );
}
