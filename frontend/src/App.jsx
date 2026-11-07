import { useEffect, useRef, useState } from "react";
import { getHistory, getStatus, resetChat, sendMessage } from "./api.js";

const SUGGESTIONS = [
  "Do I have any unread emails?",
  "Summarize my latest unread email",
  "List my unread emails",
];

const TOOL_LABELS = {
  list_unread_emails: "Checked unread emails",
  summarize_email: "Read email",
};

function ToolChip({ item }) {
  const failed = item.ok === false;
  const label = TOOL_LABELS[item.name] || item.name;
  const uid = item.args?.uid ? ` #${item.args.uid}` : "";
  return (
    <div className={`tool ${failed ? "tool-error" : ""}`}>
      <span className="tool-dot" />
      <span className="tool-label">{label + uid}</span>
      {item.summary && <span className="tool-summary">· {item.summary}</span>}
    </div>
  );
}

function Message({ item }) {
  if (item.role === "tool") return <ToolChip item={item} />;
  return (
    <div className={`msg msg-${item.role} ${item.error ? "msg-error" : ""}`}>
      <div className="bubble">{item.content}</div>
    </div>
  );
}

export default function App() {
  const [items, setItems] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null);
  const endRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    getStatus().then(setStatus).catch(() => setStatus({ offline: true }));
    getHistory()
      .then((h) => setItems(h.items))
      .catch(() => {});
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [items, busy]);

  async function send(text) {
    text = text.trim();
    if (!text || busy) return;
    setInput("");
    setItems((prev) => [...prev, { role: "user", content: text }]);
    setBusy(true);
    try {
      const { items: added } = await sendMessage(text);
      setItems((prev) => [...prev, ...added]);
    } catch (e) {
      setItems((prev) => [
        ...prev,
        { role: "assistant", content: e.message, error: true },
      ]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  async function clear() {
    if (busy) return;
    await resetChat().catch(() => {});
    setItems([]);
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  }

  const offline = status?.offline;
  const misconfigured = status && !offline && !status.configured;

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <div className="logo">N</div>
          <div>
            <h1>Noi</h1>
            <p className="sub">
              {offline
                ? "Backend unreachable"
                : status
                ? `${status.imap_user || "no account"} · ${status.model}`
                : "Connecting…"}
            </p>
          </div>
        </div>
      </header>

      {(offline || misconfigured) && (
        <div className="banner">
          {offline
            ? "Can't reach the API. Start it with: uvicorn server:app --app-dir src --port 8000"
            : "IMAP settings are missing. Check IMAP_HOST, IMAP_USER and IMAP_PASSWORD in .env."}
        </div>
      )}

      <main className="thread">
        {items.length === 0 && (
          <div className="empty">
            <h2>What would you like to do with your inbox?</h2>
            <p>I can list your latest unread emails and summarize any of them.</p>
            <div className="chips">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip" onClick={() => send(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {items.map((item, i) => (
          <Message key={i} item={item} />
        ))}
        {busy && (
          <div className="msg msg-assistant">
            <div className="bubble typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </main>

      <footer className="composer">
        <textarea
          ref={inputRef}
          rows={1}
          value={input}
          placeholder="Ask Noi…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          autoFocus
        />
        <button className="send" onClick={() => send(input)} disabled={busy || !input.trim()}>
          Send
        </button>
      </footer>
    </div>
  );
}
