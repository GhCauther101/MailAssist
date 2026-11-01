import json
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel

import graph as node
from llm import CHAT_MODEL
from envar import IMAP_HOST, IMAP_USER, IMAP_PASSWORD

app = FastAPI(title="MailAssist")

_state = {"messages": []}
_lock = threading.Lock()  # one conversation -> one request at a time

DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


class ChatRequest(BaseModel):
    message: str

def _text(content) -> str:
    """Message content can be a str or a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b if isinstance(b, str) else b.get("text", "") for b in content
        )
    return str(content or "")

def _tool_summary(name: str, raw: str):
    """Return (ok, one-line summary) for a tool result."""
    raw = _text(raw)
    try:
        data = json.loads(raw)
    except ValueError:
        data = None

    if isinstance(data, dict) and data.get("status") == "error":
        return False, data.get("message", "Error")
    if name == "list_unread_emails" and isinstance(data, dict):
        n = data.get("count", 0)
        return True, f"{n} unread email{'' if n == 1 else 's'}"
    if name == "summarize_email" and isinstance(data, dict):
        return True, data.get("subject") or "Email retrieved"
    if raw.startswith(("Could not", "Invalid", "No email found")):
        return False, raw
    return True, "Done"

def _serialize(messages) -> list:
    """Convert LangChain messages into UI items: user / assistant / tool."""
    items, pending = [], {}
    for m in messages:
        if isinstance(m, HumanMessage):
            items.append({"role": "user", "content": _text(m.content)})
        elif isinstance(m, AIMessage):
            for call in m.tool_calls or []:
                item = {
                    "role": "tool",
                    "name": call["name"],
                    "args": call.get("args", {}),
                    "ok": None,
                    "summary": "",
                }
                pending[call["id"]] = item
                items.append(item)
            text = _text(m.content).strip()
            if text:
                items.append({"role": "assistant", "content": text})
        elif isinstance(m, ToolMessage):
            item = pending.get(m.tool_call_id)
            if item:
                item["ok"], item["summary"] = _tool_summary(item["name"], m.content)
    return items

@app.get("/api/status")
def status():
    return {
        "model": CHAT_MODEL,
        "imap_host": IMAP_HOST,
        "imap_user": IMAP_USER,
        "configured": all([IMAP_HOST, IMAP_USER, IMAP_PASSWORD]),
    }

@app.get("/api/history")
def history():
    with _lock:
        return {"items": _serialize(_state["messages"])}

@app.post("/api/chat")
def chat(req: ChatRequest):
    print("here is a chat endpoint")
    text = req.message.strip()
    if not text:
        raise HTTPException(400, "Message is empty.")

    with _lock:
        before = list(_state["messages"])
        try:
            result = node.graph.invoke(
                {"messages": before + [HumanMessage(content=text)]}
            )
        except Exception as e:  # Ollama down, IMAP failure, ...
            raise HTTPException(502, f"{type(e).__name__}: {e}")

        _state["messages"] = result["messages"]
        # Everything after the user's new message = this turn's activity
        new = result["messages"][len(before) + 1:]
        # ToolMessages need their AI call for pairing, so serialize the
        # whole turn together.
        return {"items": _serialize(new)}

@app.post("/api/reset")
def reset():
    with _lock:
        _state["messages"] = []
    return {"ok": True}

if DIST.exists():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}")
    def spa(path: str):
        f = DIST / path
        return FileResponse(f if path and f.is_file() else DIST / "index.html")
