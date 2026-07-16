"use client";

import type { ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

export function FeatureToggle({
  tenantId,
  feature,
  enabled,
}: {
  tenantId: string;
  feature: string;
  enabled: boolean;
}) {
  const router = useRouter();
  return (
    <label className="checkbox-row">
      <input
        type="checkbox"
        checked={enabled}
        onChange={async (event: ChangeEvent<HTMLInputElement>) => {
          await clientApi(
            `/tenants/${tenantId}/features/${encodeURIComponent(feature)}?enabled=${event.target.checked}`,
            { method: "PATCH" },
          );
          router.refresh();
        }}
      />
      {enabled ? "Enabled" : "Disabled"}
    </label>
  );
}
