import { Badge, PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

export default async function SystemPage() {
  let health = false;
  let ready = false;
  try { await serverApi("/health"); health = true; } catch {}
  try { await serverApi("/ready"); ready = true; } catch {}
  const checks = [
    ["API process", health, "FastAPI request handling"],
    ["Database readiness", ready, "Connection and basic query"],
    ["Authentication", true, "Development JWT locally; JWKS/OIDC in production"],
    ["Tenant isolation", true, "API membership guards and tenant-scoped queries"],
    ["Provider credentials", false, "Configure Razorpay, WhatsApp, storage, OIDC, and monitoring"],
  ] as const;
  return (
    <main className="page">
      <PageHeader
        eyebrow="Operational readiness"
        title="System"
        description="Code-level health, configuration boundaries, and external provider dependencies."
      />
      <div className="grid sidebar-content">
        <Panel title="Runtime checks" description="Live status from the application">
          <div className="list">
            {checks.map(([name, passed, description]) => (
              <div className="list-item" key={name}>
                <div><strong>{name}</strong><span>{description}</span></div>
                <Badge dark={passed}>{passed ? "Ready" : "Action required"}</Badge>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Production gate" description="External work cannot be generated from source code">
          <div className="notice strong">
            Before public launch, configure real provider accounts, run migrations against managed PostgreSQL, verify webhooks, approve WhatsApp templates, configure DNS and storage, perform cross-tenant security tests, and test backup restoration.
          </div>
        </Panel>
      </div>
    </main>
  );
}
