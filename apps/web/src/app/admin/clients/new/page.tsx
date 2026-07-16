import Link from "next/link";
import { NewClientForm } from "@/components/admin/NewClientForm";
import { PageHeader, Panel } from "@/components/shared/UI";

export default function NewClientPage() {
  return (
    <main className="page">
      <PageHeader
        eyebrow="Client onboarding"
        title="Create a workspace"
        description="This creates the tenant, website, first draft, credit account, notification settings, and feature controls in one transaction."
        actions={<Link className="button secondary" href="/admin/clients">Cancel</Link>}
      />
      <div className="grid sidebar-content">
        <Panel title="Business profile" description="Enter verified client information">
          <NewClientForm />
        </Panel>
        <Panel title="What happens next" description="Automatic workspace setup">
          <div className="list">
            {[
              ["01", "Tenant isolation", "Every client-owned record is scoped to this workspace."],
              ["02", "Editable draft", "A structured template and content snapshot are generated."],
              ["03", "Operations account", "Credits, messaging settings, domains, and features are initialized."],
              ["04", "Controlled launch", "Nothing is public until review, approval, and publishing."],
            ].map(([number, title, copy]) => (
              <div className="list-item" key={number}>
                <div><strong>{number} · {title}</strong><span>{copy}</span></div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </main>
  );
}
