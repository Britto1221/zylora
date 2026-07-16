"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

type CreateResponse = { tenant: { id: string } };

export function NewClientForm() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    try {
      const result = await clientApi<CreateResponse>("/tenants", {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          legal_name: form.get("legalName") || null,
          industry: form.get("industry"),
          owner_name: form.get("ownerName") || null,
          email: form.get("email") || null,
          phone: form.get("phone") || null,
          whatsapp_number: form.get("whatsapp") || null,
          address: form.get("address") || null,
          template_key: form.get("template"),
        }),
      });
      router.push(`/admin/clients/${result.tenant.id}/overview`);
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create client.");
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="stack">
      {error ? <div className="error">{error}</div> : null}
      <div className="field-grid">
        <div className="field">
          <label htmlFor="name">Business name</label>
          <input className="input" id="name" name="name" required maxLength={180} />
        </div>
        <div className="field">
          <label htmlFor="legalName">Legal name</label>
          <input className="input" id="legalName" name="legalName" maxLength={220} />
        </div>
        <div className="field">
          <label htmlFor="industry">Industry</label>
          <select className="select" id="industry" name="industry" defaultValue="general">
            <option value="school">School</option>
            <option value="coaching">Coaching centre</option>
            <option value="clinic">Clinic</option>
            <option value="agency">Agency</option>
            <option value="general">Local business</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="template">Starting template</label>
          <select className="select" id="template" name="template" defaultValue="general">
            <option value="school">School</option>
            <option value="coaching">Coaching centre</option>
            <option value="clinic">Clinic</option>
            <option value="agency">Agency</option>
            <option value="general">Local business</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="ownerName">Owner or contact person</label>
          <input className="input" id="ownerName" name="ownerName" maxLength={180} />
        </div>
        <div className="field">
          <label htmlFor="email">Client email</label>
          <input className="input" id="email" name="email" type="email" />
        </div>
        <div className="field">
          <label htmlFor="phone">Phone</label>
          <input className="input" id="phone" name="phone" />
        </div>
        <div className="field">
          <label htmlFor="whatsapp">WhatsApp number</label>
          <input className="input" id="whatsapp" name="whatsapp" />
        </div>
        <div className="field full">
          <label htmlFor="address">Address</label>
          <textarea className="textarea" id="address" name="address" />
        </div>
      </div>
      <div className="actions">
        <button className="button" type="submit" disabled={busy}>
          {busy ? "Creating client…" : "Create client workspace"}
        </button>
      </div>
    </form>
  );
}
