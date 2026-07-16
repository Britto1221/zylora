import Link from "next/link";
import { AnalyticsBeacon } from "@/components/public/AnalyticsBeacon";
import { ChatWidget } from "@/components/public/ChatWidget";
import { LeadForm } from "@/components/public/LeadForm";
import type { PublishedWebsite, WebsiteSection } from "./types";

function text(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function objectArray(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => Boolean(item && typeof item === "object"))
    : [];
}

function Section({ section, siteId }: { section: WebsiteSection; siteId: string }) {
  const content = section.content ?? {};
  if (section.type === "hero") {
    return (
      <section className="site-section site-hero" id={section.id}>
        <div>
          <p className="eyebrow">{text(content.eyebrow)}</p>
          <h1>{text(content.heading, "Welcome")}</h1>
          <p className="site-copy">{text(content.body)}</p>
          <div className="actions" style={{ marginTop: 28 }}>
            <a className="site-button" href={text(content.primaryHref, "#contact")}>{text(content.primaryButton, "Contact us")}</a>
            {content.secondaryButton ? <a className="button secondary" href={text(content.secondaryHref, "#services")}>{text(content.secondaryButton)}</a> : null}
          </div>
        </div>
        <div>
          {content.imageUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={text(content.imageUrl)}
              alt={text(content.imageAlt)}
              style={{ width: "100%", minHeight: 420, objectFit: "cover", borderRadius: "var(--site-radius)" }}
            />
          ) : (
            <div style={{
              aspectRatio: "4 / 5", borderRadius: "var(--site-radius)",
              background: "linear-gradient(145deg, var(--site-surface), color-mix(in srgb, var(--site-primary) 12%, var(--site-bg)))",
              border: "1px solid color-mix(in srgb, var(--site-text) 12%, transparent)",
            }} />
          )}
        </div>
      </section>
    );
  }

  if (section.type === "services") {
    const items = objectArray(content.items);
    return (
      <section className="site-section" id={section.id}>
        <p className="eyebrow">{text(content.eyebrow, "Services")}</p>
        <h2 style={{ fontSize: "clamp(34px, 5vw, 62px)", letterSpacing: "-.05em" }}>{text(content.heading)}</h2>
        <p className="site-copy">{text(content.body)}</p>
        <div className="site-card-grid">
          {items.map((item, index) => (
            <article className="site-card" key={`${text(item.title)}-${index}`}>
              <p className="eyebrow">{String(index + 1).padStart(2, "0")}</p>
              <h3 style={{ fontSize: 20 }}>{text(item.title)}</h3>
              <p className="site-copy">{text(item.body)}</p>
            </article>
          ))}
        </div>
      </section>
    );
  }

  if (section.type === "about") {
    return (
      <section className="site-section" id={section.id}>
        <div className="grid two">
          <div><p className="eyebrow">{text(content.eyebrow, "About")}</p><h2 style={{ fontSize: "clamp(34px, 5vw, 62px)", letterSpacing: "-.05em" }}>{text(content.heading)}</h2></div>
          <div><p className="site-copy">{text(content.body)}</p><div className="list">{stringArray(content.points).map((point) => <div className="list-item" key={point}><strong>{point}</strong></div>)}</div></div>
        </div>
      </section>
    );
  }

  if (section.type === "testimonials") {
    return (
      <section className="site-section" id={section.id}>
        <p className="eyebrow">{text(content.eyebrow, "Testimonials")}</p>
        <h2 style={{ fontSize: "clamp(34px, 5vw, 62px)", letterSpacing: "-.05em" }}>{text(content.heading)}</h2>
        <div className="site-card-grid">
          {objectArray(content.items).map((item, index) => (
            <blockquote className="site-card" key={index} style={{ margin: 0 }}>
              <p style={{ fontSize: 18, lineHeight: 1.55 }}>“{text(item.quote)}”</p>
              <footer><strong>{text(item.name)}</strong><span className="cell-sub">{text(item.role)}</span></footer>
            </blockquote>
          ))}
        </div>
      </section>
    );
  }

  if (section.type === "faq") {
    return (
      <section className="site-section" id={section.id}>
        <p className="eyebrow">{text(content.eyebrow, "FAQ")}</p>
        <h2 style={{ fontSize: "clamp(34px, 5vw, 62px)", letterSpacing: "-.05em" }}>{text(content.heading)}</h2>
        <div className="list" style={{ marginTop: 28 }}>
          {objectArray(content.items).map((item, index) => (
            <details className="site-card" key={index}>
              <summary style={{ cursor: "pointer", fontWeight: 700 }}>{text(item.question)}</summary>
              <p className="site-copy" style={{ marginTop: 16 }}>{text(item.answer)}</p>
            </details>
          ))}
        </div>
      </section>
    );
  }

  if (section.type === "lead-form") {
    const fields = stringArray(content.fields);
    return (
      <section className="site-section" id={section.id}>
        <div className="grid two">
          <div><p className="eyebrow">{text(content.eyebrow, "Contact")}</p><h2 style={{ fontSize: "clamp(34px, 5vw, 62px)", letterSpacing: "-.05em" }}>{text(content.heading)}</h2><p className="site-copy">{text(content.body)}</p></div>
          <LeadForm siteId={siteId} fields={fields} submitLabel={text(content.submitLabel, "Send enquiry")} successMessage={text(content.successMessage, "Thank you. Your enquiry has been received.")} />
        </div>
      </section>
    );
  }

  return null;
}

export function WebsiteRenderer({ website }: { website: PublishedWebsite }) {
  const theme = website.theme;
  const content = website.content;
  const sections = (content.sections ?? []).filter((section) => section.visible !== false);
  const footer = content.footer ?? {};
  return (
    <div
      className="public-site"
      style={{
        "--site-primary": theme.primaryColor,
        "--site-accent": theme.accentColor ?? theme.primaryColor,
        "--site-bg": theme.backgroundColor,
        "--site-surface": theme.surfaceColor ?? "#f5f5f5",
        "--site-text": theme.textColor,
        "--site-muted": theme.mutedColor ?? "#71717a",
        "--site-heading": theme.headingFont,
        "--site-body": theme.bodyFont,
        "--site-radius": `${theme.radius ?? 14}px`,
        "--site-spacing": `${theme.sectionSpacing ?? 80}px`,
      } as React.CSSProperties}
    >
      {website.preview ? <div className="notice strong" style={{ borderRadius: 0, textAlign: "center" }}>Private preview · not indexed</div> : null}
      <nav className="site-nav">
        <a href="#home" style={{ fontWeight: 800, letterSpacing: "-.04em" }}>{content.businessName ?? "Business"}</a>
        <div className="site-nav-links">
          {(content.navigation ?? []).map((item) => <a href={item.href} key={item.href}>{item.label}</a>)}
        </div>
      </nav>
      <main id="home">
        {sections.map((section) => <Section section={section} siteId={website.siteId} key={section.id} />)}
      </main>
      <footer className="site-footer">
        <div className="site-footer-inner grid two">
          <div><strong>{content.businessName}</strong><p>{text(footer.summary)}</p></div>
          <div><p>{text(footer.email)}</p><p>{text(footer.phone)}</p><p>{text(footer.address)}</p></div>
        </div>
      </footer>
      {!website.preview && website.features?.analytics !== false ? <AnalyticsBeacon tenantId={website.tenantId} siteId={website.siteId} /> : null}
      {!website.preview && website.features?.chatbot === true ? <ChatWidget tenantId={website.tenantId} siteId={website.siteId} /> : null}
    </div>
  );
}
