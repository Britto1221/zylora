"use client";

import type { ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

export function LeadStatus({
  tenantId,
  leadId,
  value,
}: {
  tenantId: string;
  leadId: string;
  value: string;
}) {
  const router = useRouter();
  return (
    <select
      className="select"
      value={value}
      aria-label="Lead status"
      onChange={async (event: ChangeEvent<HTMLSelectElement>) => {
        await clientApi(`/leads/tenant/${tenantId}/${leadId}`, {
          method: "PATCH",
          body: JSON.stringify({ status: event.target.value }),
        });
        router.refresh();
      }}
      style={{ minHeight: 32, width: 130, paddingBlock: 4 }}
    >
      {["NEW", "CONTACTED", "QUALIFIED", "FOLLOW_UP", "CONVERTED", "LOST", "SPAM"].map((status) => <option key={status}>{status}</option>)}
    </select>
  );
}
