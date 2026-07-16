"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  ["overview", "Overview"],
  ["content", "Content"],
  ["website", "Website"],
  ["publishing", "Publishing"],
  ["leads", "Leads"],
  ["notifications", "WhatsApp"],
  ["credits", "Credits"],
  ["domains", "Domains"],
  ["seo", "SEO"],
  ["documents", "Documents"],
  ["assets", "Assets"],
  ["chatbot", "Chatbot"],
  ["analytics", "Analytics"],
  ["changes", "Changes"],
  ["invoices", "Invoices"],
  ["access", "Access"],
  ["audit", "Audit"],
];

export function ClientTabs({ tenantId }: { tenantId: string }) {
  const pathname = usePathname();
  return (
    <nav className="client-tabs" aria-label="Client modules">
      {tabs.map(([segment, label]) => {
        const href = `/admin/clients/${tenantId}/${segment}`;
        return (
          <Link
            href={href}
            className="client-tab"
            data-active={pathname === href}
            key={segment}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
