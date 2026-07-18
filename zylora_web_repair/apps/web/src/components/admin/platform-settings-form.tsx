"use client";

import { useState, type FormEvent } from "react";
import type { PlatformSettings } from "@/lib/site-settings";

type Props = { initialSettings: PlatformSettings };

type Status = { type: "idle" | "saving" | "success" | "error"; message: string };

export function PlatformSettingsForm({ initialSettings }: Props) {
  const [email, setEmail] = useState(initialSettings.zyloraContactEmail);
  const [accessKey, setAccessKey] = useState("");
  const [status, setStatus] = useState<Status>({ type: "idle", message: "" });

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus({ type: "saving", message: "Updating Zylora’s public email…" });

    try {
      const response = await fetch("/api/super-admin/platform-settings", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(accessKey ? { "x-zylora-settings-key": accessKey } : {}),
        },
        body: JSON.stringify({ zyloraContactEmail: email }),
      });
      const payload = (await response.json()) as { error?: string };
      if (!response.ok) {
        throw new Error(payload.error ?? "Unable to save Zylora settings.");
      }
      setStatus({
        type: "success",
        message: "Zylora’s landing-page email has been updated.",
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
        <label className="settings-field-wide">
          <span>Zylora public contact email</span>
          <input
            required
            type="email"
            maxLength={254}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <small>
            This email is used by the main landing-page CTA and displayed in the footer.
          </small>
        </label>

        <label className="settings-field-wide">
          <span>Super-admin settings key</span>
          <input
            type="password"
            autoComplete="current-password"
            placeholder="Optional during local development"
            value={accessKey}
            onChange={(event) => setAccessKey(event.target.value)}
          />
          <small>
            Production uses <code>ZYLORA_SUPER_ADMIN_SETTINGS_KEY</code>.
          </small>
        </label>
      </div>

      <div className="settings-form-actions">
        <button className="button button-primary" disabled={status.type === "saving"}>
          {status.type === "saving" ? "Saving…" : "Update Zylora email"}
        </button>
        <a className="button button-secondary" href="/" target="_blank">
          Preview Zylora landing page
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
