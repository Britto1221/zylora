"use client";

import { useState, type FormEvent } from "react";
import type { TenantSiteSettings } from "@/lib/site-settings";

type Props = {
  slug: string;
  initialSettings: TenantSiteSettings;
};

type Status = { type: "idle" | "saving" | "success" | "error"; message: string };

export function TenantSiteSettingsForm({ slug, initialSettings }: Props) {
  const [form, setForm] = useState({
    businessName: initialSettings.businessName,
    email: initialSettings.email,
    phone: initialSettings.phone,
    address: initialSettings.address,
  });
  const [accessKey, setAccessKey] = useState("");
  const [status, setStatus] = useState<Status>({ type: "idle", message: "" });

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ type: "saving", message: "Saving landing-page contact details…" });

    try {
      const response = await fetch(`/api/admin/sites/${encodeURIComponent(slug)}/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(accessKey ? { "x-zylora-settings-key": accessKey } : {}),
        },
        body: JSON.stringify(form),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) {
        throw new Error(payload.error ?? "Unable to save settings.");
      }
      setStatus({
        type: "success",
        message: "Landing-page contact details updated successfully.",
      });
    } catch (error) {
      setStatus({
        type: "error",
        message: error instanceof Error ? error.message : "Unable to save settings.",
      });
    }
  }

  return (
    <form className="settings-form" onSubmit={handleSubmit}>
      <div className="settings-form-grid">
        <label>
          <span>Business name</span>
          <input
            required
            minLength={2}
            maxLength={120}
            value={form.businessName}
            onChange={(event) =>
              setForm((current) => ({ ...current, businessName: event.target.value }))
            }
          />
        </label>

        <label>
          <span>Landing-page email</span>
          <input
            required
            type="email"
            maxLength={254}
            value={form.email}
            onChange={(event) =>
              setForm((current) => ({ ...current, email: event.target.value }))
            }
          />
        </label>

        <label>
          <span>Phone number</span>
          <input
            required
            type="tel"
            minLength={5}
            maxLength={32}
            value={form.phone}
            onChange={(event) =>
              setForm((current) => ({ ...current, phone: event.target.value }))
            }
          />
        </label>

        <label className="settings-field-wide">
          <span>Address</span>
          <textarea
            required
            minLength={5}
            maxLength={300}
            rows={4}
            value={form.address}
            onChange={(event) =>
              setForm((current) => ({ ...current, address: event.target.value }))
            }
          />
        </label>

        <label className="settings-field-wide">
          <span>Admin settings key</span>
          <input
            type="password"
            autoComplete="current-password"
            placeholder="Optional during local development"
            value={accessKey}
            onChange={(event) => setAccessKey(event.target.value)}
          />
          <small>
            Production uses <code>ZYLORA_ADMIN_SETTINGS_KEY</code>. Local development
            allows saving when the environment variable is not configured.
          </small>
        </label>
      </div>

      <div className="settings-form-actions">
        <button className="button button-primary" disabled={status.type === "saving"}>
          {status.type === "saving" ? "Saving…" : "Save contact details"}
        </button>
        <a className="button button-secondary" href={`/sites/${slug}`} target="_blank">
          Preview landing page
        </a>
      </div>

      {status.message ? (
        <p className={`settings-status settings-status-${status.type}`} role="status">
          {status.message}
        </p>
      ) : null}
    </form>
  );
}
