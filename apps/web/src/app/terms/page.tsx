import { LegalPage } from "@/components/legal/LegalPage";

export default function TermsPage() {
  const entity = process.env.LEGAL_ENTITY_NAME ?? "Zylora";
  const jurisdiction = process.env.LEGAL_JURISDICTION ?? "India";
  return <LegalPage title="Terms of Service" updated="17 July 2026">
    <p>These terms govern use of the Zylora platform and managed website services supplied by {entity}. A signed proposal, invoice, or service agreement may add project-specific terms.</p>
    <h2>Accounts and authorization</h2><p>Users must provide accurate information, secure their credentials, and access only businesses they are authorized to manage. Account sharing, abuse, unlawful content, credential harvesting, and attempts to bypass tenant boundaries are prohibited.</p>
    <h2>Managed websites and revisions</h2><p>Project scope, included revision rounds, delivery requirements, custom development, and ongoing changes are defined in the applicable quotation. Client-supplied content must be lawful and licensed.</p>
    <h2>Domains</h2><p>Domains should be registered in the client’s legal name. Renewal reminders may be sent 60, 30, 15, and 7 days before expiry. The client remains responsible for payment and renewal after the final reminder. Domain funds are separate from messaging credits.</p>
    <h2>Messaging credits</h2><p>Credits are non-transferable service units, have no cash-withdrawal value, and are used only for eligible Zylora services. At zero balance, messaging pauses while websites, lead storage, and dashboards remain available.</p>
    <h2>Third-party services</h2><p>Payments, messaging, hosting, identity, storage, and AI features depend on third-party providers and their rules. Zylora is not responsible for provider outages or account restrictions outside its reasonable control.</p>
    <h2>Suspension, liability, and disputes</h2><p>Access may be suspended for non-payment, security threats, unlawful use, or material breach. Liability is limited to the extent permitted by law and excludes indirect loss. These terms are governed by the laws applicable in {jurisdiction}, subject to mandatory consumer rights.</p>
  </LegalPage>;
}
