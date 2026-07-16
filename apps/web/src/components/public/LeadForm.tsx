"use client";

import { FormEvent, useState } from "react";

export function LeadForm({
  siteId,
  fields,
  submitLabel,
  successMessage,
}: {
  siteId: string;
  fields: string[];
  submitLabel: string;
  successMessage: string;
}) {
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("sending");
    const form = new FormData(event.currentTarget);
    const response = await fetch(
      `/api/public/leads/public`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          site_id: siteId,
          name: form.get("name"),
          email: form.get("email") || null,
          phone: form.get("phone") || null,
          service: form.get("service") || null,
          preferred_contact: form.get("preferredContact") || null,
          message: form.get("message") || null,
          whatsapp_consent: form.get("whatsappConsent") === "on",
          marketing_consent: form.get("marketingConsent") === "on",
          source: "website",
          metadata: {
            website: form.get("website") || "",
            path: window.location.pathname,
            campaign: Object.fromEntries(new URLSearchParams(window.location.search)),
          },
        }),
      },
    );
    setState(response.ok ? "sent" : "error");
    if (response.ok) event.currentTarget.reset();
  }

  if (state === "sent") return <div className="success">{successMessage}</div>;

  return (
    <form className="site-form" onSubmit={submit}>
      <input name="website" tabIndex={-1} autoComplete="off" style={{ display: "none" }} aria-hidden="true" />
      {fields.includes("name") ? <input className="input" name="name" placeholder="Your name" required /> : null}
      {fields.includes("email") ? <input className="input" name="email" type="email" placeholder="Email address" /> : null}
      {fields.includes("phone") ? <input className="input" name="phone" placeholder="Phone number" /> : null}
      {fields.includes("service") ? <input className="input" name="service" placeholder="Service required" /> : null}
      {fields.includes("message") ? <textarea className="textarea" name="message" placeholder="Tell us what you need" /> : null}
      {fields.includes("whatsappConsent") ? (
        <label className="checkbox-row">
          <input name="whatsappConsent" type="checkbox" />
          I agree to receive a WhatsApp acknowledgement about this enquiry.
        </label>
      ) : null}
      <button className="site-button" type="submit" disabled={state === "sending"}>
        {state === "sending" ? "Sending…" : submitLabel}
      </button>
      {state === "error" ? <div className="error">The enquiry could not be submitted. Please contact the business directly.</div> : null}
    </form>
  );
}
