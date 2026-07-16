"use client";

import { useEffect } from "react";

export function AnalyticsBeacon({ tenantId, siteId }: { tenantId: string; siteId: string }) {
  useEffect(() => {
    const sessionKey = "zylora_session";
    const sessionId = sessionStorage.getItem(sessionKey) ?? crypto.randomUUID();
    sessionStorage.setItem(sessionKey, sessionId);
    fetch(
      `/api/public/analytics/public`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_id: tenantId,
          site_id: siteId,
          session_id: sessionId,
          event_type: "page_view",
          path: window.location.pathname,
          referrer: document.referrer || null,
          metadata: {},
        }),
        keepalive: true,
      },
    ).catch(() => undefined);
  }, [tenantId, siteId]);
  return null;
}
