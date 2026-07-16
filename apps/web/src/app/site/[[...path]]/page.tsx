import { headers } from "next/headers";
import { notFound } from "next/navigation";

import { apiFetch } from "@/lib/api/client";
import { WebsiteRenderer } from "@/site-templates/shared/renderer";
import type { PublishedWebsite } from "@/site-templates/shared/types";

type ApiSite = {
  site_id: string;
  version_id: string;
  tenant_id: string;
  template_key: "school" | "clinic" | "coaching";
  content: {
    tenantSlug?: string;
    sections?: PublishedWebsite["sections"];
  };
  theme: PublishedWebsite["theme"];
};

export default async function PublicTenantSite() {
  const requestHeaders = await headers();
  const host =
    requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host");

  if (!host) {
    notFound();
  }

  try {
    const site = await apiFetch<ApiSite>(
      `/sites/public/resolve?host=${encodeURIComponent(host)}`,
    );

    return (
      <WebsiteRenderer
        website={{
          tenantSlug: site.content.tenantSlug ?? site.tenant_id,
          templateKey: site.template_key,
          theme: site.theme,
          sections: site.content.sections ?? [],
        }}
      />
    );
  } catch {
    notFound();
  }
}
