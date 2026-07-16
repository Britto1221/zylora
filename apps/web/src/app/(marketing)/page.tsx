import Link from "next/link";

const capabilities = [
  ["01", "Managed websites", "Structured templates, controlled drafts, approvals, publishing, and rollback."],
  ["02", "Lead operations", "Every valid enquiry is stored before optional messaging begins."],
  ["03", "WhatsApp follow-up", "Independent business and visitor messages with prepaid USD credits."],
  ["04", "Organic growth", "Version-aware SEO audits, reviewed recommendations, and client reporting."],
];

export default function MarketingPage() {
  return (
    <main style={{ background: "#050505", color: "white", minHeight: "100vh" }}>
      <nav className="site-nav" style={{ borderBottom: "1px solid #1f1f1f" }}>
        <strong style={{ letterSpacing: "-.04em" }}>Zylora</strong>
        <div className="site-nav-links">
          <a href="#system">System</a><a href="#model">Model</a><Link href="/login">Admin login</Link>
        </div>
      </nav>
      <section className="site-section site-hero" style={{ minHeight: "82vh" }}>
        <div>
          <p className="eyebrow" style={{ color: "#777" }}>Managed growth infrastructure</p>
          <h1 style={{ color: "white" }}>More than a website. A complete client operation.</h1>
          <p style={{ color: "#888", maxWidth: 650, lineHeight: 1.75 }}>
            Zylora combines premium landing pages, lead capture, client dashboards,
            optional WhatsApp follow-up, SEO intelligence, and controlled custom development.
          </p>
          <div className="actions" style={{ marginTop: 28 }}>
            <a className="button" style={{ background: "white", color: "black", borderColor: "white" }} href="#contact">Start a project</a>
            <Link className="button" style={{ borderColor: "#333", background: "#111" }} href="/login">Open console</Link>
          </div>
        </div>
        <div style={{ aspectRatio: "4/5", border: "1px solid #252525", borderRadius: 24, background: "radial-gradient(circle at 40% 25%, #252525, #080808 55%)", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: "12%", border: "1px solid #353535", borderRadius: "50%" }} />
          <div style={{ position: "absolute", inset: "28%", border: "1px solid #3f3f3f", borderRadius: "50%" }} />
        </div>
      </section>
      <section className="site-section" id="system">
        <p className="eyebrow" style={{ color: "#777" }}>One operating system</p>
        <h2 style={{ color: "white", fontSize: "clamp(40px,6vw,74px)", letterSpacing: "-.06em" }}>Designed to convert attention into managed growth.</h2>
        <div className="site-card-grid">
          {capabilities.map(([number, title, body]) => (
            <article className="site-card" style={{ borderColor: "#242424" }} key={number}>
              <p className="eyebrow" style={{ color: "#666" }}>{number}</p>
              <h3 style={{ color: "white", fontSize: 20 }}>{title}</h3>
              <p style={{ color: "#888", lineHeight: 1.65 }}>{body}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="site-section" id="model">
        <div className="grid two">
          <div><p className="eyebrow" style={{ color: "#777" }}>Commercial model</p><h2 style={{ color: "white", fontSize: "clamp(40px,6vw,74px)", letterSpacing: "-.06em" }}>Clear fees. No forced monthly plan.</h2></div>
          <div className="list">
            {[
              ["Website creation", "One-time project fee"],
              ["Standard .com domain", "$19 per year when eligible"],
              ["WhatsApp messaging", "Prepaid usage credits"],
              ["Future modifications", "Quoted separately"],
              ["Growth retainer", "Optional after trust is established"],
            ].map(([title, detail]) => <div className="list-item" style={{ borderColor: "#222" }} key={title}><strong style={{ color: "white" }}>{title}</strong><span style={{ color: "#777" }}>{detail}</span></div>)}
          </div>
        </div>
      </section>
      <section className="site-section" id="contact" style={{ textAlign: "center" }}>
        <p className="eyebrow" style={{ color: "#777" }}>Build with precision</p>
        <h2 style={{ color: "white", fontSize: "clamp(44px,7vw,88px)", letterSpacing: "-.07em" }}>Your business deserves a system, not another forgotten page.</h2>
      </section>
    </main>
  );
}
