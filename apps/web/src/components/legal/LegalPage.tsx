import Link from "next/link";

export function LegalPage({ title, updated, children }: { title: string; updated: string; children: React.ReactNode }) {
  return <main className="legal-shell">
    <header className="legal-header"><Link href="/" className="brand"><span className="brand-mark">Z</span><strong>Zylora</strong></Link><nav><Link href="/privacy">Privacy</Link><Link href="/terms">Terms</Link><Link href="/refund-policy">Refunds</Link></nav></header>
    <article className="legal-document"><p className="eyebrow">Legal</p><h1>{title}</h1><p className="muted">Last updated: {updated}</p>{children}</article>
  </main>;
}
