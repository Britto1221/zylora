"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { href: "/admin/dashboard", label: "Overview", icon: "01" },
  { href: "/admin/clients", label: "Clients", icon: "02" },
  { href: "/admin/system", label: "System", icon: "03" },
];

export function AdminShell({
  children,
  email = "admin@zylora.dev",
}: {
  children: React.ReactNode;
  email?: string;
}) {
  const pathname = usePathname();
  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <Link href="/admin/dashboard" className="brand">
          <span className="brand-mark">Z</span>
          <span className="brand-copy">
            <strong>Zylora</strong>
            <span>Operations console</span>
          </span>
        </Link>

        <div className="sidebar-section">Workspace</div>
        <nav className="sidebar-nav" aria-label="Administration">
          {navigation.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                href={item.href}
                className="sidebar-link"
                data-active={active}
                key={item.href}
              >
                <span className="sidebar-icon">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-section">Quick access</div>
        <nav className="sidebar-nav">
          <Link href="/admin/clients/new" className="sidebar-link" data-active={pathname === "/admin/clients/new"}>
            <span className="sidebar-icon">+</span><span>New client</span>
          </Link>
          <Link href="/" className="sidebar-link">
            <span className="sidebar-icon">↗</span><span>Marketing site</span>
          </Link>
        </nav>

        <div className="sidebar-footer">
          <div className="account-chip">
            <span className="avatar">BK</span>
            <div>
              <strong>Super admin</strong>
              <span>{email}</span>
            </div>
          </div>
        </div>
      </aside>

      <section className="admin-main">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Zylora</span><span>/</span><strong>Administration</strong>
          </div>
          <div className="topbar-actions">
            <Link className="button secondary small" href="/api/auth/logout">Sign out</Link>
          </div>
        </header>
        {children}
      </section>
    </div>
  );
}
