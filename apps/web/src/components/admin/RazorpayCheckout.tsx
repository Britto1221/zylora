"use client";

import { useEffect, useState } from "react";

type Pack = { id: string; label: string; credit_usd: string; charged_currency: string; charged_amount_minor: number };
declare global { interface Window { Razorpay?: new (options: Record<string, unknown>) => { open(): void } } }

export function RazorpayCheckout({ tenantId }: { tenantId: string }) {
  const [packs, setPacks] = useState<Pack[]>([]); const [message, setMessage] = useState(""); const [busy, setBusy] = useState("");
  useEffect(() => { fetch("/api/backend/payments/packs").then(r => r.json()).then(data => setPacks(data.items ?? [])).catch(() => setMessage("Unable to load credit packs.")); }, []);
  async function ensureScript() {
    if (window.Razorpay) return true;
    return await new Promise<boolean>((resolve) => { const script=document.createElement("script"); script.src="https://checkout.razorpay.com/v1/checkout.js"; script.onload=()=>resolve(true); script.onerror=()=>resolve(false); document.body.appendChild(script); });
  }
  async function buy(pack: Pack) {
    setBusy(pack.id); setMessage("");
    const response=await fetch(`/api/backend/payments/${tenantId}/orders`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({pack_id:pack.id}) });
    const data=await response.json();
    if (!response.ok) { setMessage(data.detail ?? "Order creation failed."); setBusy(""); return; }
    if (data.order.simulated) { setMessage("Development order created. Production checkout activates after Razorpay credentials are configured."); setBusy(""); return; }
    if (!(await ensureScript()) || !window.Razorpay) { setMessage("Payment checkout could not load."); setBusy(""); return; }
    const checkout=new window.Razorpay({ key:data.key_id, amount:data.order.amount, currency:data.order.currency, name:"Zylora", description:pack.label, order_id:data.order.id, handler:async (result: Record<string,string>) => {
      const verify=await fetch(`/api/backend/payments/${tenantId}/verify-checkout`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(result)});
      setMessage(verify.ok ? "Payment verified. Credits will appear after provider capture confirmation." : "Payment verification failed; no credits were issued."); setBusy("");
    }, modal:{ondismiss:()=>setBusy("")} });
    checkout.open();
  }
  return <div className="credit-packs">{packs.map(pack => <button className="credit-pack" disabled={Boolean(busy)} key={pack.id} onClick={()=>buy(pack)}><strong>${pack.credit_usd}</strong><span>{(pack.charged_amount_minor/100).toLocaleString(undefined,{style:"currency",currency:pack.charged_currency})}</span><small>{busy===pack.id?"Opening…":"Buy credits"}</small></button>)}{message?<p className="notice">{message}</p>:null}</div>;
}
