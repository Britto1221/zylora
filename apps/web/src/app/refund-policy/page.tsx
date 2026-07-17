import { LegalPage } from "@/components/legal/LegalPage";

export default function RefundPolicyPage() {
  const days = process.env.REFUND_WINDOW_DAYS ?? "7";
  return <LegalPage title="Refund and Cancellation Policy" updated="17 July 2026">
    <h2>Website projects</h2><p>Before work begins, cancellation eligibility follows the quotation. After discovery, design, development, domain purchase, or other committed work begins, completed work and non-recoverable third-party costs are not refundable. Approved refunds are reduced by work already performed.</p>
    <h2>Messaging credits</h2><p>Unused credits may be reviewed for refund within {days} days of purchase where legally required and where no provider cost or promotional restriction applies. Used, transferred, bonus, expired, or fraud-associated credits are not refundable.</p>
    <h2>Domains and third-party charges</h2><p>Domain registrations, renewals, premium names, payment fees, messaging charges, and other irreversible provider costs are generally non-refundable once submitted.</p>
    <h2>Failed or duplicate payments</h2><p>Verified duplicate charges and payments that fail without delivering the purchased service will be investigated and corrected. Refund timing depends on the payment provider and issuing bank.</p>
    <h2>Requests</h2><p>Submit the invoice number, payment reference, reason, and supporting information to the configured legal contact email. This policy does not remove rights that cannot legally be waived.</p>
  </LegalPage>;
}
