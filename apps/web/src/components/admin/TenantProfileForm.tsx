"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

type Tenant = {
  id: string;
  name: string;
  legal_name?: string | null;
  industry: string;
  owner_name?: string | null;
  email?: string | null;
  phone?: string | null;
  whatsapp_number?: string | null;
  address?: string | null;
  is_active: boolean;
  onboarding_complete: boolean;
};

export function TenantProfileForm({ tenant }: { tenant: Tenant }) {
  const router = useRouter();
  const [state, setState] = useState<"idle" | "saving" | "saved">("idle");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("saving");
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      await clientApi(`/tenants/${tenant.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: form.get("name"),
          legal_name: form.get("legalName") || null,
          industry: form.get("industry"),
          owner_name: form.get("ownerName") || null,
          email: form.get("email") || null,
          phone: form.get("phone") || null,
          whatsapp_number: form.get("whatsapp") || null,
          address: form.get("address") || null,
          is_active: form.get("active") === "on",
          onboarding_complete: form.get("onboardingComplete") === "on",
        }),
      });
      setState("saved");
      router.refresh();
      window.setTimeout(() => setState("idle"), 1800);
    } catch (reason) {
      setState("idle");
      setError(reason instanceof Error ? reason.message : "Unable to save.");
    }
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error ? <div className="error">{error}</div> : null}
      {state === "saved" ? <div className="success">Client profile saved.</div> : null}
      <div className="field-grid">
        <div className="field"><label htmlFor="name">Business name</label><input className="input" id="name" name="name" defaultValue={tenant.name} required /></div>
        <div className="field"><label htmlFor="legalName">Legal name</label><input className="input" id="legalName" name="legalName" defaultValue={tenant.legal_name ?? ""} /></div>
        <div className="field">
          <label htmlFor="industry">Industry</label>
          <select className="select" id="industry" name="industry" defaultValue={tenant.industry}>
            <option value="school">School</option><option value="coaching">Coaching centre</option>
            <option value="clinic">Clinic</option><option value="agency">Agency</option><option value="general">Local business</option>
          </select>
        </div>
        <div className="field"><label htmlFor="ownerName">Owner or contact</label><input className="input" id="ownerName" name="ownerName" defaultValue={tenant.owner_name ?? ""} /></div>
        <div className="field"><label htmlFor="email">Email</label><input className="input" id="email" name="email" type="email" defaultValue={tenant.email ?? ""} /></div>
        <div className="field"><label htmlFor="phone">Phone</label><input className="input" id="phone" name="phone" defaultValue={tenant.phone ?? ""} /></div>
        <div className="field"><label htmlFor="whatsapp">WhatsApp</label><input className="input" id="whatsapp" name="whatsapp" defaultValue={tenant.whatsapp_number ?? ""} /></div>
        <div className="field full"><label htmlFor="address">Address</label><textarea className="textarea" id="address" name="address" defaultValue={tenant.address ?? ""} /></div>
      </div>
      <div className="grid two">
        <label className="checkbox-row"><input type="checkbox" name="active" defaultChecked={tenant.is_active} /> Client account is active</label>
        <label className="checkbox-row"><input type="checkbox" name="onboardingComplete" defaultChecked={tenant.onboarding_complete} /> Onboarding is complete</label>
      </div>
      <div className="actions"><button className="button" disabled={state === "saving"}>{state === "saving" ? "Saving…" : "Save client profile"}</button></div>
    </form>
  );
}
