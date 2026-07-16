import { headers } from "next/headers";
import { notFound } from "next/navigation";
import { WebsiteRenderer } from "@/site-templates/shared/renderer";
import type { PublishedWebsite } from "@/site-templates/shared/types";

const API_URL =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1";

export const dynamic = "force-dynamic";

export default async function PublicSitePage() {
  const requestHeaders = await headers();
  const host = (
    requestHeaders.get("x-zylora-host") ??
    requestHeaders.get("x-forwarded-host") ??
    requestHeaders.get("host") ??
    ""
  ).split(":")[0];

  const response = await fetch(`${API_URL}/sites/public/resolve?host=${encodeURIComponent(host)}`, {
    cache: "no-store",
  });
  if (!response.ok) notFound();
  const site = await response.json();
  const website: PublishedWebsite = {
    siteId: site.siteId,
    tenantId: site.tenantId,
    tenantSlug: site.tenantSlug,
    templateKey: site.templateKey,
    content: site.content,
    theme: site.theme,
    seo: site.seo,
    features: site.features ?? {},
  };
  return <WebsiteRenderer website={website} />;
}
