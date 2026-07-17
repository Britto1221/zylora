import { LegalPage } from "@/components/legal/LegalPage";

export default function PrivacyPage() {
  const entity = process.env.LEGAL_ENTITY_NAME ?? "Zylora";
  const email = process.env.LEGAL_CONTACT_EMAIL ?? "Configure LEGAL_CONTACT_EMAIL";
  return <LegalPage title="Privacy Policy" updated="17 July 2026">
    <h2>Who controls your data</h2><p>{entity} operates the Zylora platform. Privacy requests may be sent to {email}. Client businesses remain responsible for the information they collect through their own websites and lead forms.</p>
    <h2>Information we process</h2><p>We process account identifiers, business profile content, website configuration, leads submitted by visitors, consent records, payment references, usage events, security logs, uploaded files, chatbot conversations, and support requests.</p>
    <h2>Purposes and lawful handling</h2><p>Information is used to provide contracted services, authenticate users, publish websites, store and route leads, send requested notifications, prevent abuse, process payments, maintain records, improve reliability, and comply with applicable law. Marketing messages require an appropriate consent basis.</p>
    <h2>Sharing and processors</h2><p>Data may be processed by configured hosting, identity, payment, messaging, email, analytics, monitoring, database, and storage providers. We do not sell personal data. Providers receive only the information required to perform their service.</p>
    <h2>Retention and security</h2><p>Records are retained for the service relationship, legal obligations, dispute handling, and configured backup periods. Controls include encryption in transit, tenant authorization, restricted secrets, audit logging, malware scanning, backups, and incident monitoring.</p>
    <h2>Your rights</h2><p>Subject to applicable law, individuals may request access, correction, erasure, grievance review, consent withdrawal, or information about processing. Requests will be verified before action is taken.</p>
    <h2>International processing and changes</h2><p>Some providers may process information outside India under their contractual safeguards. Material policy changes will be posted here with an updated date.</p>
  </LegalPage>;
}
