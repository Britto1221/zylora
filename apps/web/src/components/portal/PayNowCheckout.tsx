"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open(): void };
  }
}

type Invoice = {
  id: string;
  number: string;
  currency: string;
  total_minor: number;
};

export function PayNowCheckout({ tenantId, invoice }: { tenantId: string; invoice: Invoice }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const router = useRouter();

  async function ensureScript() {
    if (window.Razorpay) return true;
    return new Promise<boolean>((resolve) => {
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  }

  async function pay() {
    setBusy(true);
    setMessage("");
    try {
      const data = await clientApi<{
        order: { id: string; amount: number; currency: string; simulated?: boolean };
        key_id: string;
      }>(`/billing/${tenantId}/pay-order`, { method: "POST" });
      if (data.order.simulated) {
        setMessage("Development payment order created. Configure Razorpay credentials to open live checkout.");
        return;
      }
      if (!(await ensureScript()) || !window.Razorpay) {
        throw new Error("Razorpay checkout could not load.");
      }
      new window.Razorpay({
        key: data.key_id,
        amount: data.order.amount,
        currency: data.order.currency,
        name: "Zylora",
        description: `Recurring invoice ${invoice.number}`,
        order_id: data.order.id,
        handler: async (result: Record<string, string>) => {
          await clientApi(`/billing/${tenantId}/verify-checkout`, {
            method: "POST",
            body: JSON.stringify({
              razorpay_order_id: result.razorpay_order_id,
              razorpay_payment_id: result.razorpay_payment_id,
              razorpay_signature: result.razorpay_signature,
            }),
          });
          setMessage("Payment submitted. Access will restore after the verified capture webhook is received.");
          router.refresh();
        },
        theme: { color: "#111111" },
      }).open();
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "Payment could not start.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="stack">
      <div className="metric-card">
        <span>Amount due</span>
        <strong>{invoice.currency} {(invoice.total_minor / 100).toFixed(2)}</strong>
        <small className="mono">{invoice.number}</small>
      </div>
      <button className="button" type="button" disabled={busy} onClick={pay}>
        {busy ? "Preparing secure checkout…" : "Pay now"}
      </button>
      {message ? <div className="notice">{message}</div> : null}
      <p className="cell-sub">Your public website and lead capture remain online while the portal is restricted.</p>
    </div>
  );
}
