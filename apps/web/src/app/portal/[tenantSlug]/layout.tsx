import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { PortalShell } from "@/components/portal/PortalShell";
import { serverApi } from "@/lib/api/server";

type BillingStatus = {
  billingStatus: "current" | "warned" | "restricted";
  daysPastDue: number;
};

export default async function PortalLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ tenantSlug: string }>;
}) {
  const { tenantSlug } = await params;
  const data = await serverApi<{ tenant: { id: string; name: string } }>(`/tenants/slug/${tenantSlug}`);
  const billing = await serverApi<BillingStatus>(`/billing/${data.tenant.id}/status`);
  const requestHeaders = await headers();
  const pathname = requestHeaders.get("x-zylora-pathname") ?? "";
  const payNowPath = `/portal/${tenantSlug}/pay-now`;

  if (billing.billingStatus === "restricted" && pathname !== payNowPath) {
    redirect(payNowPath);
  }

  return (
    <PortalShell
      slug={tenantSlug}
      clientName={data.tenant.name}
      billingStatus={billing.billingStatus}
      daysPastDue={billing.daysPastDue}
    >
      {children}
    </PortalShell>
  );
}
