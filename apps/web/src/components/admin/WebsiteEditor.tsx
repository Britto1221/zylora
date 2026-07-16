"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

type Draft = {
  id: string;
  content_snapshot: Record<string, unknown>;
  theme_snapshot: Record<string, unknown>;
  seo_snapshot: Record<string, unknown>;
};

function sectionContent(content: Record<string, unknown>, type: string): Record<string, unknown> {
  const sections = Array.isArray(content.sections) ? content.sections as Array<Record<string, unknown>> : [];
  const section = sections.find((item) => item.type === type);
  return (section?.content as Record<string, unknown>) ?? {};
}

export function WebsiteEditor({
  tenantId,
  templateKey,
  draft,
  mode = "content",
}: {
  tenantId: string;
  templateKey: string;
  draft: Draft;
  mode?: "content" | "theme";
}) {
  const router = useRouter();
  const initialContent = draft.content_snapshot;
  const initialTheme = draft.theme_snapshot;
  const initialSeo = draft.seo_snapshot;
  const hero = useMemo(() => sectionContent(initialContent, "hero"), [initialContent]);
  const footer = (initialContent.footer as Record<string, unknown>) ?? {};

  const [contentJson, setContentJson] = useState(JSON.stringify(initialContent, null, 2));
  const [themeJson, setThemeJson] = useState(JSON.stringify(initialTheme, null, 2));
  const [seoJson, setSeoJson] = useState(JSON.stringify(initialSeo, null, 2));
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSaved("");
    const form = new FormData(event.currentTarget);
    try {
      const content = JSON.parse(contentJson) as Record<string, unknown>;
      const sections = Array.isArray(content.sections)
        ? content.sections.map((section) => {
            const item = { ...(section as Record<string, unknown>) };
            if (item.type === "hero") {
              item.content = {
                ...((item.content as Record<string, unknown>) ?? {}),
                heading: form.get("heroHeading"),
                body: form.get("heroBody"),
                primaryButton: form.get("heroButton"),
              };
            }
            return item;
          })
        : [];
      content.businessName = form.get("businessName");
      content.sections = sections;
      content.footer = {
        ...footer,
        email: form.get("footerEmail"),
        phone: form.get("footerPhone"),
        address: form.get("footerAddress"),
      };

      const result = await clientApi<{ validation: { valid: boolean; errors: string[]; warnings: string[] } }>(
        `/sites/tenant/${tenantId}/draft`,
        {
          method: "PATCH",
          body: JSON.stringify({
            template_key: form.get("template"),
            content,
            theme: JSON.parse(themeJson),
            seo: JSON.parse(seoJson),
          }),
        },
      );
      setContentJson(JSON.stringify(content, null, 2));
      setSaved(
        result.validation.valid
          ? "Draft saved and ready for review checks."
          : `Draft saved with ${result.validation.errors.length} blocking issue(s).`,
      );
      router.refresh();
    } catch (reason) {
      setError(reason instanceof SyntaxError ? "One of the JSON editors contains invalid JSON." : reason instanceof Error ? reason.message : "Unable to save draft.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error ? <div className="error">{error}</div> : null}
      {saved ? <div className="success">{saved}</div> : null}
      {mode === "content" ? (
        <>
          <div className="field-grid">
            <div className="field"><label htmlFor="businessName">Displayed business name</label><input className="input" id="businessName" name="businessName" defaultValue={String(initialContent.businessName ?? "")} required /></div>
            <div className="field">
              <label htmlFor="template">Template</label>
              <select className="select" id="template" name="template" defaultValue={templateKey}>
                <option value="school">School</option><option value="coaching">Coaching centre</option>
                <option value="clinic">Clinic</option><option value="agency">Agency</option><option value="general">Local business</option>
              </select>
            </div>
            <div className="field full"><label htmlFor="heroHeading">Hero heading</label><input className="input" id="heroHeading" name="heroHeading" defaultValue={String(hero.heading ?? "")} required /></div>
            <div className="field full"><label htmlFor="heroBody">Hero description</label><textarea className="textarea" id="heroBody" name="heroBody" defaultValue={String(hero.body ?? "")} /></div>
            <div className="field"><label htmlFor="heroButton">Primary button</label><input className="input" id="heroButton" name="heroButton" defaultValue={String(hero.primaryButton ?? "Contact us")} /></div>
            <div className="field"><label htmlFor="footerEmail">Footer email</label><input className="input" id="footerEmail" name="footerEmail" type="email" defaultValue={String(footer.email ?? "")} /></div>
            <div className="field"><label htmlFor="footerPhone">Footer phone</label><input className="input" id="footerPhone" name="footerPhone" defaultValue={String(footer.phone ?? "")} /></div>
            <div className="field"><label htmlFor="footerAddress">Footer address</label><input className="input" id="footerAddress" name="footerAddress" defaultValue={String(footer.address ?? "")} /></div>
          </div>
          <div className="field">
            <label htmlFor="contentJson">Structured section content</label>
            <span className="field-hint">Advanced editor. Sections remain typed objects rather than uncontrolled HTML.</span>
            <textarea className="textarea code" id="contentJson" value={contentJson} onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setContentJson(event.target.value)} spellCheck={false} />
          </div>
        </>
      ) : (
        <>
          <div className="field">
            <label htmlFor="themeJson">Theme tokens</label>
            <span className="field-hint">Client websites may use their own colours. The Zylora administration interface remains monochromatic.</span>
            <textarea className="textarea code" id="themeJson" value={themeJson} onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setThemeJson(event.target.value)} spellCheck={false} />
          </div>
          <div className="field">
            <label htmlFor="seoJson">SEO metadata</label>
            <textarea className="textarea code" id="seoJson" value={seoJson} onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setSeoJson(event.target.value)} spellCheck={false} />
          </div>
        </>
      )}
      {/* Keep all values available when switching modes. */}
      {mode === "content" ? (
        <>
          <textarea hidden readOnly value={themeJson} />
          <textarea hidden readOnly value={seoJson} />
        </>
      ) : (
        <>
          <input type="hidden" name="businessName" value={String(initialContent.businessName ?? "")} />
          <input type="hidden" name="template" value={templateKey} />
          <input type="hidden" name="heroHeading" value={String(hero.heading ?? "")} />
          <input type="hidden" name="heroBody" value={String(hero.body ?? "")} />
          <input type="hidden" name="heroButton" value={String(hero.primaryButton ?? "")} />
          <input type="hidden" name="footerEmail" value={String(footer.email ?? "")} />
          <input type="hidden" name="footerPhone" value={String(footer.phone ?? "")} />
          <input type="hidden" name="footerAddress" value={String(footer.address ?? "")} />
        </>
      )}
      <div className="actions"><button className="button" disabled={busy}>{busy ? "Saving draft…" : "Save draft"}</button></div>
    </form>
  );
}
