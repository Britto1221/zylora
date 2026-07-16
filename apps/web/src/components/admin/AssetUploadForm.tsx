"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { clientApi } from "@/lib/api/client";

type Presign = {
  asset: { id: string };
  upload: { url: string; method: string; headers: Record<string, string>; localDevelopment?: boolean };
};

export function AssetUploadForm({ tenantId }: { tenantId: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setProgress("Preparing secure upload…"); setError("");
    const form = new FormData(event.currentTarget);
    const file = form.get("file");
    if (!(file instanceof File)) {
      setError("Select a file."); setBusy(false); return;
    }
    try {
      const presign = await clientApi<Presign>(`/assets/${tenantId}/presign`, {
        method: "POST",
        body: JSON.stringify({
          filename: file.name,
          mime_type: file.type || "application/octet-stream",
          size_bytes: file.size,
          category: form.get("category"),
          alt_text: form.get("altText") || null,
        }),
      });
      setProgress("Uploading file…");
      if (presign.upload.localDevelopment) {
        const body = new FormData();
        body.append("file", file);
        const response = await fetch(presign.upload.url, { method: "POST", body });
        if (!response.ok) throw new Error("Local upload failed.");
      } else {
        const response = await fetch(presign.upload.url, {
          method: presign.upload.method,
          headers: presign.upload.headers,
          body: file,
        });
        if (!response.ok) throw new Error("Object storage rejected the upload.");
        await clientApi(`/assets/${tenantId}/${presign.asset.id}/complete`, {
          method: "POST",
          body: JSON.stringify({ checksum_sha256: null, public_url: null }),
        });
      }
      setProgress("Upload completed.");
      event.currentTarget.reset();
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Upload failed.");
      setProgress("");
    } finally { setBusy(false); }
  }

  return (
    <form className="stack" onSubmit={submit}>
      {progress ? <div className="success">{progress}</div> : null}
      {error ? <div className="error">{error}</div> : null}
      <div className="field-grid">
        <div className="field full"><label htmlFor="assetFile">File</label><input className="input" id="assetFile" name="file" type="file" accept=".jpg,.jpeg,.png,.webp,.svg,.pdf,.txt" required /></div>
        <div className="field"><label htmlFor="assetCategory">Category</label><select className="select" id="assetCategory" name="category"><option value="logo">Logo</option><option value="website">Website image</option><option value="document">Document</option><option value="general">General</option></select></div>
        <div className="field"><label htmlFor="altText">Alt text</label><input className="input" id="altText" name="altText" maxLength={500} /></div>
      </div>
      <button className="button" disabled={busy}>{busy ? "Uploading…" : "Upload asset"}</button>
    </form>
  );
}
