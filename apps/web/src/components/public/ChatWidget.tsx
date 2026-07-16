"use client";

import { FormEvent, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

export function ChatWidget({ tenantId, siteId }: { tenantId: string; siteId: string }) {
  const [open, setOpen] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const question = String(form.get("question") ?? "").trim();
    if (!question) return;
    setMessages((current) => [...current, { role: "user", content: question }]);
    setBusy(true);
    event.currentTarget.reset();
    const response = await fetch(
      `/api/public/chatbot/public`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_id: tenantId,
          site_id: siteId,
          conversation_id: conversationId,
          visitor_id: sessionStorage.getItem("zylora_session"),
          question,
        }),
      },
    );
    const result = await response.json();
    setBusy(false);
    if (response.ok) {
      setConversationId(result.conversationId);
      setMessages((current) => [...current, { role: "assistant", content: result.answer }]);
    } else {
      setMessages((current) => [...current, { role: "assistant", content: "Chat is currently unavailable. Please use the contact form." }]);
    }
  }

  return (
    <div style={{ position: "fixed", right: 22, bottom: 22, zIndex: 30 }}>
      {open ? (
        <section className="panel" style={{ width: 340, maxWidth: "calc(100vw - 32px)", marginBottom: 10 }}>
          <div className="panel-head"><div><h2>Ask the business</h2><p>Answers use verified documents</p></div><button className="button ghost small" onClick={() => setOpen(false)}>Close</button></div>
          <div className="panel-body" style={{ maxHeight: 330, overflowY: "auto" }}>
            <div className="stack">
              {messages.length ? messages.map((message, index) => (
                <div className={message.role === "assistant" ? "notice" : "notice strong"} key={index}>{message.content}</div>
              )) : <div className="notice">Ask a question about the business’s services, FAQs, or published information.</div>}
            </div>
          </div>
          <form className="panel-body actions" onSubmit={submit} style={{ borderTop: "1px solid #e5e5e5" }}>
            <input className="input" name="question" placeholder="Type a question…" required />
            <button className="button small" disabled={busy}>{busy ? "…" : "Send"}</button>
          </form>
        </section>
      ) : null}
      <button className="button" onClick={() => setOpen((value) => !value)}>{open ? "Hide chat" : "Ask a question"}</button>
    </div>
  );
}
