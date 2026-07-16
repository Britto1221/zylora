import { PageHeader, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

export default async function PortalAccount({ params }: { params: Promise<{ tenantSlug: string }> }) {
  const { tenantSlug } = await params;
  const { tenant } = await serverApi<{ tenant: { name: string; email?: string | null; owner_name?: string | null; phone?: string | null } }>(`/tenants/slug/${tenantSlug}`);
  return (
    <main className="page">
      <PageHeader eyebrow="Identity and access" title="Account" description="Business profile and production identity-provider settings." />
      <div className="grid two">
        <Panel title="Business contact" description="Managed by your Zylora administrator">
          <div className="list"><div className="list-item"><div><strong>Business</strong><span>{tenant.name}</span></div></div><div className="list-item"><div><strong>Contact</strong><span>{tenant.owner_name ?? "Not assigned"}</span></div></div><div className="list-item"><div><strong>Email</strong><span>{tenant.email ?? "Not set"}</span></div></div><div className="list-item"><div><strong>Phone</strong><span>{tenant.phone ?? "Not set"}</span></div></div></div>
        </Panel>
        <Panel title="Password and sessions" description="Handled by the verified identity provider">
          <p className="lede">Use the identity provider’s signed password-reset and session-management flow. Zylora never stores plaintext passwords.</p>
          <a className="button secondary" href={process.env.NEXT_PUBLIC_AUTH_PASSWORD_RESET_URL ?? "/forgot-password"}>Manage password</a>
        </Panel>
      </div>
    </main>
  );
}
