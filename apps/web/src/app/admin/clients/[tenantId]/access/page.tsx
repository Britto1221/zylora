import { CredentialForm, InvitationForm } from "@/components/admin/AccessForms";
import { FeatureToggle } from "@/components/admin/FeatureToggle";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type TenantResponse = {
  tenant: { id: string; email?: string | null };
  features: Record<string, boolean>;
};
type AccessResponse = {
  members: Array<{ id: string; email: string; role: string; is_active: boolean; created_at: string }>;
  invitations: Array<{ id: string; email: string; role: string; status: string; expires_at: string; created_at: string }>;
  credentials: Array<{ id: string; provider: string; masked: string; status: string; lastVerifiedAt?: string | null }>;
};

export default async function AccessPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const [data, access] = await Promise.all([
    serverApi<TenantResponse>(`/tenants/${tenantId}`),
    serverApi<AccessResponse>(`/access/${tenantId}/members`),
  ]);
  return (
    <div className="stack">
      <div className="grid two">
        <Panel title="Invite client user" description="Signed, expiring, tenant-scoped invitation">
          <InvitationForm tenantId={tenantId} />
        </Panel>
        <Panel title="Client-provided AI key" description="Encrypted at rest and never returned after save">
          <CredentialForm tenantId={tenantId} />
        </Panel>
      </div>
      <div className="grid two">
        <Panel title="Feature access" description="Enable modules independently">
          <div className="list">
            {Object.entries(data.features).map(([feature, enabled]) => (
              <div className="list-item" key={feature}>
                <div><strong>{feature.replaceAll("_", " ")}</strong><span>Tenant-scoped feature flag</span></div>
                <FeatureToggle tenantId={tenantId} feature={feature} enabled={enabled} />
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Encrypted credentials" description="Masked provider access">
          {access.credentials.length ? <div className="list">
            {access.credentials.map((credential) => (
              <div className="list-item" key={credential.id}>
                <div><strong>{credential.provider}</strong><span className="mono">{credential.masked} · {credential.status}</span></div>
                <div className="actions">
                  <ActionButton path={`/access/${tenantId}/credentials/${credential.id}/test`} label="Test" />
                  <ActionButton path={`/access/${tenantId}/credentials/${credential.id}`} method="DELETE" label="Remove" confirm={`Remove the ${credential.provider} key?`} />
                </div>
              </div>
            ))}
          </div> : <Empty title="No client API keys" description="Zylora-managed provider credentials remain server-side. Add a BYOK credential only when required." />}
        </Panel>
      </div>
      <Panel title="Active members" description="Roles are enforced in the API and database queries" flush>
        {access.members.length ? <div className="table-wrap"><table><thead><tr><th>User</th><th>Role</th><th>Status</th><th>Added</th><th /></tr></thead><tbody>
          {access.members.map((member) => <tr key={member.id}><td>{member.email}</td><td><Badge>{member.role}</Badge></td><td><Badge dark={member.is_active}>{member.is_active ? "Active" : "Revoked"}</Badge></td><td><DateText value={member.created_at} /></td><td>{member.is_active ? <ActionButton path={`/access/${tenantId}/members/${member.id}`} method="DELETE" label="Revoke" confirm={`Revoke access for ${member.email}?`} /> : null}</td></tr>)}
        </tbody></table></div> : <Empty title="No client members" description="Invite a client administrator or read-only viewer." />}
      </Panel>
      <Panel title="Pending and historical invitations" description="Tokens are hashed; plaintext tokens are shown only in local development" flush>
        {access.invitations.length ? <div className="table-wrap"><table><thead><tr><th>Email</th><th>Role</th><th>Status</th><th>Expires</th><th>Created</th></tr></thead><tbody>
          {access.invitations.map((invite) => <tr key={invite.id}><td>{invite.email}</td><td>{invite.role}</td><td><Badge>{invite.status}</Badge></td><td><DateText value={invite.expires_at} /></td><td><DateText value={invite.created_at} /></td></tr>)}
        </tbody></table></div> : <Empty title="No invitations" description="Client user invitations will appear here." />}
      </Panel>
    </div>
  );
}
