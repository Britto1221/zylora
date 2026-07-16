import type { PublishedWebsite } from "./types";

export function WebsiteRenderer({ website }: { website: PublishedWebsite }) {
  return (
    <div
      style={
        {
          "--primary": website.theme.primaryColor,
          "--accent": website.theme.accentColor,
          background: website.theme.backgroundColor,
          minHeight: "100vh",
          fontFamily: website.theme.bodyFont,
        } as React.CSSProperties
      }
    >
      {website.sections
        .filter((section) => section.visible)
        .map((section) => (
          <section key={section.id} style={{ padding: "64px 24px" }}>
            <h2>{String(section.content.heading ?? section.type)}</h2>
            <p>{String(section.content.body ?? "")}</p>
          </section>
        ))}
    </div>
  );
}
