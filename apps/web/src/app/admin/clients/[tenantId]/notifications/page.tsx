import { NotificationSettingsForm } from "@/components/admin/OperationsForms";
import { ActionButton } from "@/components/shared/ActionButton";
import { Badge, DateText, Empty, Panel } from "@/components/shared/UI";
import { serverApi } from "@/lib/api/server";

type Data = {
  settings: {
    business_enabled: boolean; visitor_enabled: boolean;
    business_template: string; visitor_template: string;
    business_charge_micro_usd: number; visitor_charge_micro_usd: number;
  };
  jobs: Array<{
    id: string; recipient_type: string; recipient: string; template_name: string;
    status: string; attempts: number; charge_micro_usd: number; failure_reason?: string | null; created_at: string;
  }>;
  total: number;
};

export default async function NotificationsPage({ params }: { params: Promise<{ tenantId: string }> }) {
  const { tenantId } = await params;
  const data = await serverApi<Data>(`/notifications/${tenantId}`);
  return (
    <div className="stack">
      <div className="grid sidebar-content">
        <Panel title="WhatsApp policy" description="Business and visitor messages are independent">
          <NotificationSettingsForm tenantId={tenantId} settings={data.settings} />
        </Panel>
        <Panel title="Failure isolation" description="Lead capture remains available">
          <div className="notice strong">At zero credits, website traffic, lead forms, lead storage, dashboards, and exports continue. Only chargeable WhatsApp jobs are skipped.</div>
        </Panel>
      </div>
      <Panel title="Message jobs" description={`${data.total} job${data.total === 1 ? "" : "s"} recorded`} flush>
        {data.jobs.length ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Recipient</th><th>Template</th><th>Charge</th><th>Status</th><th>Attempts</th><th>Created</th><th /></tr></thead>
              <tbody>
                {data.jobs.map((job) => (
                  <tr key={job.id}>
                    <td><span className="cell-title">{job.recipient_type}</span><span className="cell-sub mono">{job.recipient}</span></td>
                    <td className="mono">{job.template_name}</td>
                    <td>${(job.charge_micro_usd / 1_000_000).toFixed(4)}</td>
                    <td><Badge dark={["DELIVERED","READ"].includes(job.status)}>{job.status}</Badge>{job.failure_reason ? <span className="cell-sub">{job.failure_reason}</span> : null}</td>
                    <td>{job.attempts}</td>
                    <td><DateText value={job.created_at} /></td>
                    <td>{["FAILED","SKIPPED_INSUFFICIENT_CREDITS"].includes(job.status) ? <ActionButton path={`/notifications/${tenantId}/jobs/${job.id}/retry`} label="Retry" /> : null}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <Empty title="No message jobs" description="Jobs are created atomically when valid public leads are stored." />}
      </Panel>
    </div>
  );
}
