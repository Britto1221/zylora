"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

function useMutation() {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function run(path: string, method: "POST" | "PATCH" | "DELETE", body?: unknown) {
    setBusy(true);
    setMessage("");
    setError("");
    try {
      const result = await clientApi<unknown>(path, {
        method,
        body: body === undefined ? undefined : JSON.stringify(body),
      });
      setMessage("Saved successfully.");
      router.refresh();
      return result;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Request failed.");
      throw reason;
    } finally {
      setBusy(false);
    }
  }
  return { busy, message, error, run };
}

function Feedback({ message, error }: { message: string; error: string }) {
  return (
    <>
      {message ? <div className="success">{message}</div> : null}
      {error ? <div className="error">{error}</div> : null}
    </>
  );
}

export function CreditTopUpForm({ tenantId }: { tenantId: string }) {
  const mutation = useMutation();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await mutation.run(`/credits/${tenantId}/manual-top-up`, "POST", {
      amount_usd: form.get("amount"),
      description: form.get("description"),
      external_reference: form.get("reference") || null,
    });
    event.currentTarget.reset();
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback message={mutation.message} error={mutation.error} />
      <div className="field-grid">
        <div className="field"><label htmlFor="amount">USD amount</label><input className="input" id="amount" name="amount" inputMode="decimal" placeholder="25.00" required /></div>
        <div className="field"><label htmlFor="reference">Payment reference</label><input className="input" id="reference" name="reference" placeholder="UPI, bank, or receipt ID" /></div>
        <div className="field full"><label htmlFor="description">Description</label><input className="input" id="description" name="description" defaultValue="Manual prepaid WhatsApp credit top-up" required /></div>
      </div>
      <button className="button" disabled={mutation.busy}>{mutation.busy ? "Adding credits…" : "Add verified credits"}</button>
    </form>
  );
}

export function DomainForm({ tenantId }: { tenantId: string }) {
  const mutation = useMutation();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await mutation.run(`/domains/${tenantId}`, "POST", {
      hostname: form.get("hostname"),
      domain_type: form.get("type"),
      is_primary: form.get("primary") === "on",
      registered_to_client: form.get("clientOwned") === "on",
      expires_at: form.get("expiresAt") ? new Date(String(form.get("expiresAt"))).toISOString() : null,
      renewal_price_usd: form.get("price") || "19.00",
    });
    event.currentTarget.reset();
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback message={mutation.message} error={mutation.error} />
      <div className="field-grid">
        <div className="field"><label htmlFor="hostname">Hostname</label><input className="input mono" id="hostname" name="hostname" placeholder="clientbusiness.com" required /></div>
        <div className="field"><label htmlFor="type">Domain type</label><select className="select" id="type" name="type"><option value="custom">Custom domain</option><option value="subdomain">Zylora subdomain</option></select></div>
        <div className="field"><label htmlFor="expiresAt">Expiry date</label><input className="input" id="expiresAt" name="expiresAt" type="date" /></div>
        <div className="field"><label htmlFor="price">Annual price · USD</label><input className="input" id="price" name="price" defaultValue="19.00" /></div>
      </div>
      <div className="grid two">
        <label className="checkbox-row"><input type="checkbox" name="primary" defaultChecked /> Preferred public domain</label>
        <label className="checkbox-row"><input type="checkbox" name="clientOwned" defaultChecked /> Registered in the client’s legal name</label>
      </div>
      <button className="button" disabled={mutation.busy}>{mutation.busy ? "Adding domain…" : "Add domain"}</button>
    </form>
  );
}

type NotificationSetting = {
  business_enabled: boolean;
  visitor_enabled: boolean;
  business_template: string;
  visitor_template: string;
  business_charge_micro_usd: number;
  visitor_charge_micro_usd: number;
};

export function NotificationSettingsForm({
  tenantId,
  settings,
}: {
  tenantId: string;
  settings: NotificationSetting;
}) {
  const mutation = useMutation();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await mutation.run(`/notifications/${tenantId}/settings`, "PATCH", {
      business_enabled: form.get("businessEnabled") === "on",
      visitor_enabled: form.get("visitorEnabled") === "on",
      business_template: form.get("businessTemplate"),
      visitor_template: form.get("visitorTemplate"),
      business_charge_micro_usd: Number(form.get("businessCharge")),
      visitor_charge_micro_usd: Number(form.get("visitorCharge")),
    });
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback message={mutation.message} error={mutation.error} />
      <div className="grid two">
        <label className="checkbox-row"><input name="businessEnabled" type="checkbox" defaultChecked={settings.business_enabled} /> Notify business about new leads</label>
        <label className="checkbox-row"><input name="visitorEnabled" type="checkbox" defaultChecked={settings.visitor_enabled} /> Send visitor acknowledgements with consent</label>
      </div>
      <div className="field-grid">
        <div className="field"><label htmlFor="businessTemplate">Business template</label><input className="input mono" id="businessTemplate" name="businessTemplate" defaultValue={settings.business_template} /></div>
        <div className="field"><label htmlFor="visitorTemplate">Visitor template</label><input className="input mono" id="visitorTemplate" name="visitorTemplate" defaultValue={settings.visitor_template} /></div>
        <div className="field"><label htmlFor="businessCharge">Business charge · micro-USD</label><input className="input" id="businessCharge" name="businessCharge" type="number" min="0" defaultValue={settings.business_charge_micro_usd} /></div>
        <div className="field"><label htmlFor="visitorCharge">Visitor charge · micro-USD</label><input className="input" id="visitorCharge" name="visitorCharge" type="number" min="0" defaultValue={settings.visitor_charge_micro_usd} /></div>
      </div>
      <button className="button" disabled={mutation.busy}>{mutation.busy ? "Saving…" : "Save messaging policy"}</button>
    </form>
  );
}

export function TextDocumentForm({ tenantId }: { tenantId: string }) {
  const mutation = useMutation();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await mutation.run(`/documents/${tenantId}`, "POST", {
      name: form.get("name"),
      category: form.get("category"),
      text: form.get("text"),
    });
    event.currentTarget.reset();
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback message={mutation.message} error={mutation.error} />
      <div className="field-grid">
        <div className="field"><label htmlFor="documentName">Document name</label><input className="input" id="documentName" name="name" required /></div>
        <div className="field"><label htmlFor="documentCategory">Category</label><select className="select" id="documentCategory" name="category"><option value="brochure">Brochure</option><option value="services">Services</option><option value="faq">FAQ</option><option value="policy">Policy</option><option value="general">General</option></select></div>
        <div className="field full"><label htmlFor="documentText">Document text</label><textarea className="textarea code" id="documentText" name="text" required placeholder="Paste verified business content. It will be parsed, chunked, embedded, and indexed for the chatbot." /></div>
      </div>
      <button className="button" disabled={mutation.busy}>{mutation.busy ? "Processing…" : "Add and index document"}</button>
    </form>
  );
}

export function ChangeRequestForm({ tenantId }: { tenantId: string }) {
  const mutation = useMutation();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await mutation.run(`/changes/${tenantId}`, "POST", {
      category: form.get("category"),
      title: form.get("title"),
      description: form.get("description"),
      priority: form.get("priority"),
    });
    event.currentTarget.reset();
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback message={mutation.message} error={mutation.error} />
      <div className="field-grid">
        <div className="field"><label htmlFor="changeCategory">Category</label><select className="select" id="changeCategory" name="category"><option value="text">Text change</option><option value="image">Image change</option><option value="contact">Contact change</option><option value="section">New section</option><option value="page">New page</option><option value="design">Design modification</option><option value="feature">Custom feature</option><option value="seo">SEO work</option></select></div>
        <div className="field"><label htmlFor="priority">Priority</label><select className="select" id="priority" name="priority"><option value="NORMAL">Normal</option><option value="HIGH">High</option><option value="LOW">Low</option></select></div>
        <div className="field full"><label htmlFor="changeTitle">Request title</label><input className="input" id="changeTitle" name="title" required /></div>
        <div className="field full"><label htmlFor="changeDescription">Exact change required</label><textarea className="textarea" id="changeDescription" name="description" required /></div>
      </div>
      <button className="button" disabled={mutation.busy}>{mutation.busy ? "Submitting…" : "Create change request"}</button>
    </form>
  );
}

export function InvoiceForm({ tenantId }: { tenantId: string }) {
  const mutation = useMutation();
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await mutation.run(`/invoices/${tenantId}`, "POST", {
      currency: form.get("currency"),
      tax_minor: Number(form.get("taxMinor")),
      due_at: form.get("dueAt") ? new Date(String(form.get("dueAt"))).toISOString() : null,
      line_items: [
        {
          description: form.get("description"),
          quantity: Number(form.get("quantity")),
          unitMinor: Number(form.get("unitMinor")),
        },
      ],
    });
    event.currentTarget.reset();
  }
  return (
    <form className="stack" onSubmit={submit}>
      <Feedback message={mutation.message} error={mutation.error} />
      <div className="field-grid">
        <div className="field full"><label htmlFor="invoiceDescription">Line item</label><input className="input" id="invoiceDescription" name="description" placeholder="Landing page development" required /></div>
        <div className="field"><label htmlFor="quantity">Quantity</label><input className="input" id="quantity" name="quantity" type="number" min="1" defaultValue="1" required /></div>
        <div className="field"><label htmlFor="unitMinor">Unit amount · minor units</label><input className="input" id="unitMinor" name="unitMinor" type="number" min="0" placeholder="29900 for $299.00" required /></div>
        <div className="field"><label htmlFor="currency">Currency</label><select className="select" id="currency" name="currency"><option value="USD">USD</option><option value="INR">INR</option></select></div>
        <div className="field"><label htmlFor="taxMinor">Configured tax · minor units</label><input className="input" id="taxMinor" name="taxMinor" type="number" min="0" defaultValue="0" /></div>
        <div className="field"><label htmlFor="dueAt">Due date</label><input className="input" id="dueAt" name="dueAt" type="date" /></div>
      </div>
      <button className="button" disabled={mutation.busy}>{mutation.busy ? "Creating…" : "Create draft invoice"}</button>
    </form>
  );
}

export function SeoRunButton({ tenantId }: { tenantId: string }) {
  const mutation = useMutation();
  return (
    <span>
      <button className="button" disabled={mutation.busy} onClick={() => mutation.run(`/seo/${tenantId}/run`, "POST")}>
        {mutation.busy ? "Auditing…" : "Run SEO audit"}
      </button>
      {mutation.error ? <span className="cell-sub">{mutation.error}</span> : null}
    </span>
  );
}
