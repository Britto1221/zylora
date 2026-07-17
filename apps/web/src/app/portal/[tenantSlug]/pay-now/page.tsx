import { redirect } from "next/navigation";
import { PayNowCheckout } from "@/components/portal/PayNowCheckout";
import { Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type BillingStatus = {
  tenantId: string;
  billingStatus: "current" | "warned" | "restricted";
  daysPastDue: number;
  invoice: null | {
    id: string;
    number: string;
    currency: string;
    total_minor: number;
    due_at?: string | null;
  };
};

export default async function PayNowPage({
  params,
}: {
  params: Promise<{ tenantSlug: string }>;
}) {
  const { tenantSlug } = await params;
  const tenant = await serverApi<{ tenant: { id: string; name: string } }>(`/tenants/slug/${tenantSlug}`);
  const billing = await serverApi<BillingStatus>(`/billing/${tenant.tenant.id}/status`);
  if (billing.billingStatus === "current" || !billing.invoice) {
    redirect(`/portal/${tenantSlug}/dashboard`);
  }
  return (
    <div className="stack portal-pay-now">
      <Panel
        title="Payment required"
        description={`The recurring invoice is ${billing.daysPastDue} days overdue. Portal access restores after verified payment.`}
      >
        <PayNowCheckout tenantId={tenant.tenant.id} invoice={billing.invoice} />
      </Panel>
    </div>
  );
}
