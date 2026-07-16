import type { Metadata } from "next";
import { serverApi } from "@/lib/api/server";
import { WebsiteRenderer } from "@/site-templates/shared/renderer";
import type { PublishedWebsite } from "@/site-templates/shared/types";

export const metadata: Metadata = { robots: { index: false, follow: false } };

export default async function PreviewPage({
  params,
}: {
  params: Promise<{ siteVersionId: string }>;
}) {
  const { siteVersionId } = await params;
  const site = await serverApi<{
    siteId: string; versionId: string; tenantId: string; tenantSlug: string;
    templateKey: string; content: PublishedWebsite["content"]; theme: PublishedWebsite["theme"]; seo: Record<string, unknown>;
  }>(`/sites/preview/${siteVersionId}`);
  return <WebsiteRenderer website={{ ...site, preview: true }} />;
}
