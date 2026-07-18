import Link from "next/link";
import { getPlatformSettings } from "@/lib/site-settings";

export const dynamic = "force-dynamic";

const outcomes = [
  { value: "01", label: "Launch", detail: "Publish a polished business website." },
  { value: "02", label: "Capture", detail: "Turn visits into structured leads." },
  { value: "03", label: "Respond", detail: "Route enquiries to the right channel." },
  { value: "04", label: "Grow", detail: "Improve content, SEO, and conversion." },
];

const capabilities = [
  {
    number: "01",
    title: "Premium websites",
    description:
      "Structured, responsive websites designed for clarity, trust, speed, and conversion.",
    tags: ["Templates", "Publishing", "Custom domains"],
  },
  {
    number: "02",
    title: "Lead operations",
    description:
      "Capture, organize, qualify, and follow up with every enquiry from one client workspace.",
    tags: ["Lead forms", "Statuses", "Exports"],
  },
  {
    number: "03",
    title: "AI knowledge",
    description:
      "Turn approved business content into a grounded assistant that answers with context.",
    tags: ["Knowledge base", "RAG", "Guardrails"],
  },
  {
    number: "04",
    title: "Business communication",
    description:
      "Connect lead events to WhatsApp and other operational notifications without losing control.",
    tags: ["WhatsApp", "Credits", "Delivery tracking"],
  },
  {
    number: "05",
    title: "SEO intelligence",
    description:
      "Surface technical and content opportunities with clear, actionable recommendations.",
    tags: ["Audits", "Priorities", "Reports"],
  },
  {
    number: "06",
    title: "Client control",
    description:
      "Give every business a focused portal for leads, credits, reports, domains, and account access.",
    tags: ["Portal", "Billing", "Permissions"],
  },
];

const industries = [
  {
    title: "Schools & coaching",
    copy: "Admissions, enquiries, course discovery, parent questions, and conversion-focused landing pages.",
  },
  {
    title: "Clinics & wellness",
    copy: "Service discovery, appointment enquiries, trusted information, and responsive lead follow-up.",
  },
  {
    title: "Agencies & consultants",
    copy: "Premium positioning, service pages, qualification forms, and organized client acquisition.",
  },
  {
    title: "Local service businesses",
    copy: "A credible digital presence, clear offers, local enquiries, and simple operational visibility.",
  },
];

const activity = [
  { name: "New website enquiry", meta: "Organic search · 2 min ago", status: "New" },
  { name: "Consultation request", meta: "Service page · 18 min ago", status: "Qualified" },
  { name: "Course admission lead", meta: "Campaign page · 43 min ago", status: "Contacted" },
];

function BrandMark() {
  return (
    <span className="brand-mark" aria-hidden="true">
      <span />
      <span />
      <span />
    </span>
  );
}

function ArrowIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="M4 10h11M11 5l5 5-5 5" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 20 20" aria-hidden="true">
      <path d="m4 10 3.3 3.3L16 5.8" />
    </svg>
  );
}

function SparkIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2c.7 5.1 2.9 7.3 8 8-5.1.7-7.3 2.9-8 8-.7-5.1-2.9-7.3-8-8 5.1-.7 7.3-2.9 8-8Z" />
      <path d="M19 16c.3 2 1.2 2.9 3 3-1.8.2-2.7 1.1-3 3-.2-1.9-1.1-2.8-3-3 1.9-.1 2.8-1 3-3Z" />
    </svg>
  );
}

function GlobeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3c3 3.3 3 14.7 0 18M12 3c-3 3.3-3 14.7 0 18" />
    </svg>
  );
}

function MessageIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 5h14v10H9l-4 4V5Z" />
      <path d="M8 9h8M8 12h5" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 19V9M10 19V5M16 19v-7M22 19H2" />
    </svg>
  );
}

function DashboardPreview() {
  return (
    <div className="product-stage" aria-label="Zylora dashboard interface preview">
      <div className="stage-glow stage-glow-one" />
      <div className="stage-glow stage-glow-two" />

      <div className="dashboard-window">
        <div className="window-topbar">
          <div className="window-controls" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div className="window-address">app.zylora.ai/workspace</div>
          <div className="window-user">BK</div>
        </div>

        <div className="dashboard-layout">
          <aside className="dashboard-sidebar">
            <div className="sidebar-brand">
              <BrandMark />
              <strong>Zylora</strong>
            </div>

            <nav aria-label="Dashboard preview navigation">
              <span className="preview-nav active">
                <i /> Overview
              </span>
              <span className="preview-nav">
                <i /> Website
              </span>
              <span className="preview-nav">
                <i /> Leads
              </span>
              <span className="preview-nav">
                <i /> Knowledge
              </span>
              <span className="preview-nav">
                <i /> Analytics
              </span>
            </nav>

            <div className="sidebar-card">
              <span>Workspace health</span>
              <strong>All systems ready</strong>
              <div className="health-track">
                <span />
              </div>
            </div>
          </aside>

          <div className="dashboard-content">
            <div className="dashboard-heading">
              <div>
                <span className="dashboard-kicker">Friday, 17 July</span>
                <h3>Good evening, Britto.</h3>
              </div>
              <button type="button">Publish changes</button>
            </div>

            <div className="metric-grid">
              <article>
                <span>New leads</span>
                <strong>148</strong>
                <small>+18.4% this month</small>
              </article>
              <article>
                <span>Conversion</span>
                <strong>12.8%</strong>
                <small>+2.1% this month</small>
              </article>
              <article>
                <span>Website visits</span>
                <strong>4,921</strong>
                <small>+26.7% this month</small>
              </article>
            </div>

            <div className="dashboard-lower">
              <article className="chart-card">
                <div className="card-heading">
                  <div>
                    <span>Lead performance</span>
                    <strong>Growth over 30 days</strong>
                  </div>
                  <small>Last 30 days</small>
                </div>

                <div className="chart-area" aria-hidden="true">
                  <div className="chart-grid-line line-one" />
                  <div className="chart-grid-line line-two" />
                  <div className="chart-grid-line line-three" />
                  <svg viewBox="0 0 620 190" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
                        <stop offset="0%" stopColor="rgba(79, 70, 229, .28)" />
                        <stop offset="100%" stopColor="rgba(79, 70, 229, 0)" />
                      </linearGradient>
                    </defs>
                    <path
                      className="chart-fill"
                      d="M0,163 C42,155 55,116 99,127 C142,139 148,88 198,100 C246,111 266,59 310,73 C358,88 384,40 427,52 C471,64 506,22 548,31 C582,38 600,17 620,12 L620,190 L0,190 Z"
                    />
                    <path
                      className="chart-line"
                      d="M0,163 C42,155 55,116 99,127 C142,139 148,88 198,100 C246,111 266,59 310,73 C358,88 384,40 427,52 C471,64 506,22 548,31 C582,38 600,17 620,12"
                    />
                  </svg>
                  <span className="chart-dot dot-one" />
                  <span className="chart-dot dot-two" />
                  <span className="chart-dot dot-three" />
                </div>
              </article>

              <article className="activity-card">
                <div className="card-heading">
                  <div>
                    <span>Recent activity</span>
                    <strong>Latest leads</strong>
                  </div>
                  <small>View all</small>
                </div>

                <div className="activity-list">
                  {activity.map((item) => (
                    <div className="activity-item" key={item.name}>
                      <span className="activity-avatar">
                        {item.name
                          .split(" ")
                          .slice(0, 2)
                          .map((word) => word[0])
                          .join("")}
                      </span>
                      <div>
                        <strong>{item.name}</strong>
                        <small>{item.meta}</small>
                      </div>
                      <em>{item.status}</em>
                    </div>
                  ))}
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>

      <div className="floating-card floating-card-lead">
        <span className="floating-icon">
          <MessageIcon />
        </span>
        <div>
          <small>New lead captured</small>
          <strong>Consultation request</strong>
        </div>
        <span className="live-dot" />
      </div>

      <div className="floating-card floating-card-publish">
        <span className="floating-icon">
          <GlobeIcon />
        </span>
        <div>
          <small>Website status</small>
          <strong>Published successfully</strong>
        </div>
        <span className="floating-check">
          <CheckIcon />
        </span>
      </div>
    </div>
  );
}

export default async function MarketingPage() {
  const platformSettings = await getPlatformSettings();

  return (
    <div className="marketing-site">
      <header className="site-header">
        <div className="site-container header-inner">
          <Link className="brand" href="/" aria-label="Zylora home">
            <BrandMark />
            <span>Zylora</span>
          </Link>

          <nav className="desktop-nav" aria-label="Primary navigation">
            <a href="#platform">Platform</a>
            <a href="#workflow">How it works</a>
            <a href="#solutions">Solutions</a>
            <a href="#principles">Why Zylora</a>
          </nav>

          <div className="header-actions">
            <Link className="text-link" href="/login">
              Sign in
            </Link>
            <a className="button button-small button-dark" href="#contact">
              Build with Zylora
              <ArrowIcon />
            </a>
          </div>
        </div>
      </header>

      <main className="marketing-main">
        <section className="hero-section">
          <div className="hero-grid-overlay" aria-hidden="true" />
          <div className="hero-orb hero-orb-one" aria-hidden="true" />
          <div className="hero-orb hero-orb-two" aria-hidden="true" />

          <div className="site-container hero-inner">
            <div className="hero-copy">
              <div className="eyebrow">
                <span className="eyebrow-icon">
                  <SparkIcon />
                </span>
                Digital infrastructure for modern businesses
              </div>

              <h1>
                Your business deserves more than{" "}
                <span className="accent-text">just a website.</span>
              </h1>

              <p className="hero-description">
                Zylora brings your website, leads, AI knowledge, communication,
                publishing, and growth operations into one carefully managed platform.
              </p>

              <div className="hero-actions">
                <a className="button button-primary" href="#contact">
                  Start building
                  <ArrowIcon />
                </a>
                <a className="button button-secondary" href="#platform">
                  Explore the platform
                </a>
              </div>

              <div className="hero-proof">
                <div className="proof-avatars" aria-hidden="true">
                  <span>SC</span>
                  <span>CL</span>
                  <span>AG</span>
                  <span>+</span>
                </div>
                <p>
                  Designed for schools, clinics, coaching centres, agencies, and
                  ambitious local businesses.
                </p>
              </div>
            </div>

            <div className="hero-visual">
              <DashboardPreview />
            </div>
          </div>
        </section>

        <section className="outcomes-section" aria-label="Zylora operating model">
          <div className="site-container outcomes-grid">
            {outcomes.map((item) => (
              <article key={item.value}>
                <span>{item.value}</span>
                <div>
                  <strong>{item.label}</strong>
                  <p>{item.detail}</p>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="section section-intro" id="platform">
          <div className="site-container">
            <div className="section-heading section-heading-wide">
              <div>
                <span className="section-index">01 / Platform</span>
                <h2>
                  One connected system for your{" "}
                  <span>digital business.</span>
                </h2>
              </div>
              <p>
                Replace disconnected tools, fragile handoffs, and unclear ownership
                with a platform designed around the complete customer journey.
              </p>
            </div>

            <div className="capability-grid">
              {capabilities.map((capability) => (
                <article className="capability-card" key={capability.number}>
                  <div className="capability-topline">
                    <span>{capability.number}</span>
                    <span className="capability-arrow">
                      <ArrowIcon />
                    </span>
                  </div>
                  <h3>{capability.title}</h3>
                  <p>{capability.description}</p>
                  <div className="tag-list">
                    {capability.tags.map((tag) => (
                      <span key={tag}>{tag}</span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section workflow-section" id="workflow">
          <div className="site-container workflow-layout">
            <div className="workflow-copy">
              <span className="section-index">02 / Workflow</span>
              <h2>
                From business information to a{" "}
                <span>working growth system.</span>
              </h2>
              <p>
                Zylora turns approved business content into a complete public presence,
                then connects every enquiry to the tools needed to respond and improve.
              </p>

              <div className="workflow-steps">
                <article>
                  <span>01</span>
                  <div>
                    <h3>Structure the business</h3>
                    <p>
                      Organize services, content, contact details, brand assets, and
                      operational preferences.
                    </p>
                  </div>
                </article>
                <article>
                  <span>02</span>
                  <div>
                    <h3>Build and publish</h3>
                    <p>
                      Create a premium website, review changes, connect a domain, and
                      publish with control.
                    </p>
                  </div>
                </article>
                <article>
                  <span>03</span>
                  <div>
                    <h3>Capture and improve</h3>
                    <p>
                      Centralize leads, monitor outcomes, and continuously improve
                      content, SEO, and conversion.
                    </p>
                  </div>
                </article>
              </div>
            </div>

            <div className="workflow-visual" aria-label="Zylora connected workflow">
              <div className="workflow-grid" aria-hidden="true" />
              <div className="workflow-core">
                <BrandMark />
                <span>Zylora</span>
                <small>Business platform</small>
              </div>

              <div className="workflow-node node-website">
                <span className="node-icon">
                  <GlobeIcon />
                </span>
                <div>
                  <strong>Website</strong>
                  <small>Published</small>
                </div>
              </div>

              <div className="workflow-node node-leads">
                <span className="node-icon">
                  <MessageIcon />
                </span>
                <div>
                  <strong>Lead capture</strong>
                  <small>Active</small>
                </div>
              </div>

              <div className="workflow-node node-ai">
                <span className="node-icon">
                  <SparkIcon />
                </span>
                <div>
                  <strong>AI knowledge</strong>
                  <small>Grounded</small>
                </div>
              </div>

              <div className="workflow-node node-analytics">
                <span className="node-icon">
                  <ChartIcon />
                </span>
                <div>
                  <strong>Analytics</strong>
                  <small>Live</small>
                </div>
              </div>

              <svg className="workflow-lines" viewBox="0 0 680 620" aria-hidden="true">
                <path d="M340 310 C260 290 248 168 170 142" />
                <path d="M340 310 C428 284 450 164 530 136" />
                <path d="M340 310 C264 342 242 462 154 487" />
                <path d="M340 310 C424 343 453 458 542 482" />
              </svg>

              <div className="workflow-pulse pulse-one" />
              <div className="workflow-pulse pulse-two" />
            </div>
          </div>
        </section>

        <section className="section results-section">
          <div className="site-container results-layout">
            <div className="results-card">
              <div className="results-card-copy">
                <span className="section-index section-index-light">
                  Business outcomes
                </span>
                <h2>Built around what actually matters.</h2>
                <p>
                  A premium website is only the beginning. Zylora connects presentation
                  quality with measurable business operations.
                </p>
              </div>

              <div className="results-metrics">
                <article>
                  <strong>24/7</strong>
                  <span>Lead capture</span>
                </article>
                <article>
                  <strong>1</strong>
                  <span>Connected workspace</span>
                </article>
                <article>
                  <strong>100%</strong>
                  <span>Client-owned domain</span>
                </article>
              </div>
            </div>

            <div className="results-list">
              <article>
                <span>
                  <CheckIcon />
                </span>
                <div>
                  <h3>Credibility before complexity</h3>
                  <p>
                    Clear positioning, disciplined design, useful content, and fast
                    performance come before decorative technology.
                  </p>
                </div>
              </article>
              <article>
                <span>
                  <CheckIcon />
                </span>
                <div>
                  <h3>Operations behind the interface</h3>
                  <p>
                    Leads, notifications, credits, publishing, domains, and access are
                    managed as one accountable system.
                  </p>
                </div>
              </article>
              <article>
                <span>
                  <CheckIcon />
                </span>
                <div>
                  <h3>AI with business boundaries</h3>
                  <p>
                    AI uses approved context, visible usage accounting, and explicit
                    operational controls.
                  </p>
                </div>
              </article>
            </div>
          </div>
        </section>

        <section className="section industries-section" id="solutions">
          <div className="site-container">
            <div className="section-heading">
              <div>
                <span className="section-index">03 / Solutions</span>
                <h2>
                  One foundation.{" "}
                  <span>Different business realities.</span>
                </h2>
              </div>
              <p>
                Zylora keeps the core platform consistent while adapting the public
                experience and workflow to each industry.
              </p>
            </div>

            <div className="industry-list">
              {industries.map((industry, index) => (
                <article key={industry.title}>
                  <span className="industry-number">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <h3>{industry.title}</h3>
                  <p>{industry.copy}</p>
                  <span className="industry-arrow">
                    <ArrowIcon />
                  </span>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section principles-section" id="principles">
          <div className="site-container">
            <div className="principles-panel">
              <div className="principles-intro">
                <span className="section-index section-index-light">
                  04 / Principles
                </span>
                <h2>
                  Premium is not decoration. It is{" "}
                  <span>clarity, trust, and control.</span>
                </h2>
              </div>

              <div className="principle-grid">
                <article>
                  <span>01</span>
                  <h3>Designed to be understood</h3>
                  <p>
                    Every interface should make the next decision clearer, not add more
                    visual noise.
                  </p>
                </article>
                <article>
                  <span>02</span>
                  <h3>Built for ownership</h3>
                  <p>
                    Clients retain ownership of their domain, content, leads, and
                    business identity.
                  </p>
                </article>
                <article>
                  <span>03</span>
                  <h3>Operated with accountability</h3>
                  <p>
                    Publishing, credits, messages, payments, and changes are visible
                    and traceable.
                  </p>
                </article>
              </div>
            </div>
          </div>
        </section>

        <section className="section final-cta-section" id="contact">
          <div className="site-container">
            <div className="final-cta">
              <div className="final-cta-grid" aria-hidden="true" />
              <div className="cta-copy">
                <span className="section-index">Build with Zylora</span>
                <h2>
                  Turn your digital presence into a{" "}
                  <span>working business system.</span>
                </h2>
                <p>
                  Start with a premium public experience. Connect leads, communication,
                  AI knowledge, publishing, and growth when the business is ready.
                </p>
              </div>
              <div className="cta-actions">
                <a
                  className="button button-primary button-large"
                  href={`mailto:${platformSettings.zyloraContactEmail}`}
                >
                  Start a conversation
                  <ArrowIcon />
                </a>
                <small>Built for long-term business ownership.</small>
                <a className="cta-email-link" href={`mailto:${platformSettings.zyloraContactEmail}`}>
                  {platformSettings.zyloraContactEmail}
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-container footer-main">
          <div className="footer-brand">
            <Link className="brand brand-footer" href="/">
              <BrandMark />
              <span>Zylora</span>
            </Link>
            <p>
              Premium digital infrastructure for businesses that want clarity,
              control, and measurable growth.
            </p>
          </div>

          <div className="footer-links">
            <div>
              <strong>Platform</strong>
              <a href="#platform">Capabilities</a>
              <a href="#workflow">How it works</a>
              <a href="#solutions">Solutions</a>
            </div>
            <div>
              <strong>Company</strong>
              <a href="#principles">Principles</a>
              <a href="#contact">Contact</a>
              <a href={`mailto:${platformSettings.zyloraContactEmail}`}>
                {platformSettings.zyloraContactEmail}
              </a>
              <Link href="/login">Client sign in</Link>
            </div>
            <div>
              <strong>Legal</strong>
              <a href="/privacy">Privacy</a>
              <a href="/terms">Terms</a>
              <a href="/security">Security</a>
            </div>
          </div>
        </div>

        <div className="site-container footer-bottom">
          <span>© {new Date().getFullYear()} Zylora. All rights reserved.</span>
          <span>Digital business infrastructure.</span>
        </div>
      </footer>
    </div>
  );
}
