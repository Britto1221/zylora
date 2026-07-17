import { LegalPage } from "@/components/legal/LegalPage";

export default function CookiePolicyPage() {
  return <LegalPage title="Cookie Policy" updated="17 July 2026">
    <p>Zylora uses strictly necessary cookies for secure authentication, OAuth state validation, session routing, fraud prevention, and user preferences. Optional analytics or marketing storage must be enabled only after the appropriate consent mechanism is configured.</p>
    <h2>Necessary cookies</h2><p>These include secure session tokens, OAuth PKCE state, CSRF-related values, and interface preferences. Disabling them may prevent login or dashboard use.</p>
    <h2>Analytics</h2><p>First-party usage events may be collected with minimized identifiers to measure page performance and lead conversion. Client websites must display consent controls whenever required by applicable law or configured tracking.</p>
  </LegalPage>;
}
