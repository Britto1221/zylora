"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { clientApi } from "@/lib/api/client";
import { Badge, DateText } from "@/components/shared/UI";

export type ClientListItem = {
  id: string;
  name: string;
  slug: string;
  industry: string;
  owner_name?: string | null;
  email?: string | null;
  is_active: boolean;
  billing_status: "current" | "warned" | "restricted";
  operational_status: "active" | "paused";
  site_status: "live" | "draft";
  health_status: "Healthy" | "Needs attention" | "Restricted";
  health_reasons: string[];
  last_login_at?: string | null;
  created_at: string;
};

export function ClientBulkTable({ clients }: { clients: ClientListItem[] }) {
  const router = useRouter();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const selectedIds = useMemo(() => Array.from(selected), [selected]);
  const allSelected = clients.length > 0 && selected.size === clients.length;

  function toggle(id: string) {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAll() {
    setSelected(allSelected ? new Set() : new Set(clients.map((client) => client.id)));
  }

  async function jsonAction(kind: "reminder" | "override") {
    if (!selectedIds.length) return;
    const confirmation = kind === "reminder"
      ? `Send payment reminders for ${selectedIds.length} selected client(s)?`
      : `Clear billing restrictions for ${selectedIds.length} selected client(s)?`;
    if (!window.confirm(confirmation)) return;
    setBusy(kind);
    setMessage("");
    setError("");
    try {
      const path = kind === "reminder"
        ? "/admin/clients/bulk/payment-reminders"
        : "/admin/clients/bulk/clear-lockouts";
      await clientApi(path, {
        method: "POST",
        body: JSON.stringify({ tenant_ids: selectedIds }),
      });
      setMessage(kind === "reminder" ? "Payment reminders queued." : "Billing overrides applied.");
      setSelected(new Set());
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Bulk action failed.");
    } finally {
      setBusy("");
    }
  }

  async function exportSelected() {
    if (!selectedIds.length) return;
    setBusy("export");
    setMessage("");
    setError("");
    try {
      const response = await fetch("/api/backend/exports/bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tenant_ids: selectedIds }),
      });
      if (!response.ok) throw new Error(`Bulk export failed (${response.status}).`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "zylora-client-exports.zip";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
      setMessage("Standalone export package downloaded.");
      setSelected(new Set());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Bulk export failed.");
    } finally {
      setBusy("");
    }
  }

  return (
    <div>
      <div className="bulk-bar">
        <div>
          <strong>{selected.size} selected</strong>
          <span className="cell-sub">Every operation uses the same audited super-admin service as its single-client equivalent.</span>
        </div>
        <div className="actions">
          <button className="button secondary small" disabled={!selected.size || Boolean(busy)} onClick={() => jsonAction("reminder")} type="button">
            {busy === "reminder" ? "Queuing…" : "Send payment reminder"}
          </button>
          <button className="button secondary small" disabled={!selected.size || Boolean(busy)} onClick={exportSelected} type="button">
            {busy === "export" ? "Building…" : "Export self-host ZIP"}
          </button>
          <button className="button secondary small" disabled={!selected.size || Boolean(busy)} onClick={() => jsonAction("override")} type="button">
            {busy === "override" ? "Applying…" : "Clear billing lockout"}
          </button>
        </div>
      </div>
      {message ? <div className="notice">{message}</div> : null}
      {error ? <div className="error">{error}</div> : null}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th><input aria-label="Select all clients" checked={allSelected} onChange={toggleAll} type="checkbox" /></th>
              <th>Client</th><th>Health</th><th>Billing</th><th>Site</th><th>Last login</th><th>Owner</th><th />
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => (
              <tr key={client.id}>
                <td><input aria-label={`Select ${client.name}`} checked={selected.has(client.id)} onChange={() => toggle(client.id)} type="checkbox" /></td>
                <td>
                  <Link className="cell-title" href={`/admin/clients/${client.id}/overview`}>{client.name}</Link>
                  <span className="cell-sub mono">{client.slug} · {client.industry}</span>
                </td>
                <td title={client.health_reasons.join(" · ")}>
                  <Badge dark={client.health_status === "Healthy"}>{client.health_status}</Badge>
                  <span className="cell-sub health-reasons">{client.health_reasons.join(" · ")}</span>
                </td>
                <td>
                  <Badge dark={client.billing_status === "current"}>{client.billing_status}</Badge>
                  {client.operational_status === "paused" ? <span className="cell-sub">Paused manually</span> : null}
                </td>
                <td><Badge dark={client.site_status === "live"}>{client.site_status}</Badge></td>
                <td><DateText value={client.last_login_at} /></td>
                <td><span className="cell-title">{client.owner_name ?? "Not assigned"}</span><span className="cell-sub">{client.email ?? ""}</span></td>
                <td><Link className="button secondary small" href={`/admin/clients/${client.id}/overview`}>Open</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
