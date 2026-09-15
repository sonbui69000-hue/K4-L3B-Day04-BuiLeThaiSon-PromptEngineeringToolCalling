from __future__ import annotations

import argparse
import json
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Northstar Helpdesk Agent</title>
  <style>
    :root {
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #637083;
      --line: #d9dee8;
      --accent: #176b87;
      --accent-2: #2f6f4e;
      --warn: #a44913;
      --soft: #eef6f8;
      --tool: #f3f5f0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background: var(--bg);
    }

    .shell {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 380px;
      min-height: 100vh;
    }

    .main {
      display: grid;
      grid-template-rows: auto 1fr auto;
      min-height: 100vh;
      border-right: 1px solid var(--line);
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 20px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }

    h1 {
      margin: 0;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0;
    }

    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
    }

    .pill {
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 999px;
      padding: 5px 8px;
      max-width: 360px;
      overflow-wrap: anywhere;
    }

    #messages {
      padding: 18px 20px;
      overflow: auto;
    }

    .message {
      max-width: 880px;
      margin: 0 0 14px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .message.user {
      margin-left: auto;
      background: var(--soft);
      border-color: #c9e2e8;
    }

    .message.assistant {
      margin-right: auto;
    }

    .role {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .composer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 14px 20px;
      background: var(--panel);
      border-top: 1px solid var(--line);
    }

    textarea {
      width: 100%;
      min-height: 48px;
      max-height: 160px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }

    button {
      min-width: 88px;
      border: 0;
      border-radius: 8px;
      padding: 0 16px;
      color: #fff;
      background: var(--accent);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    button:disabled {
      opacity: .55;
      cursor: not-allowed;
    }

    aside {
      min-width: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      min-height: 100vh;
      background: #fbfcfd;
    }

    .side-head {
      padding: 16px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    .side-head h2 {
      margin: 0 0 8px;
      font-size: 15px;
      letter-spacing: 0;
    }

    .status {
      color: var(--muted);
      font-size: 12px;
      overflow-wrap: anywhere;
    }

    #tools {
      padding: 14px;
      overflow: auto;
    }

    .tool {
      margin-bottom: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--tool);
      overflow: hidden;
    }

    .tool-title {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      font-size: 13px;
      font-weight: 700;
    }

    .tool-title span:last-child {
      color: var(--muted);
      font-weight: 600;
    }

    details {
      padding: 8px 12px 10px;
    }

    summary {
      cursor: pointer;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
    }

    pre {
      overflow: auto;
      max-height: 280px;
      margin: 8px 0 0;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: #20242a;
      font-size: 12px;
      line-height: 1.4;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .footer {
      padding: 12px 16px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
      background: var(--panel);
      overflow-wrap: anywhere;
    }

    .empty {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .error {
      color: var(--warn);
      font-weight: 700;
    }

    @media (max-width: 860px) {
      .shell { grid-template-columns: 1fr; }
      .main { min-height: 70vh; border-right: 0; }
      aside { min-height: 46vh; border-top: 1px solid var(--line); }
      header { align-items: flex-start; flex-direction: column; }
      .composer { grid-template-columns: 1fr; }
      button { height: 44px; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <main class="main">
      <header>
        <h1>Northstar Helpdesk Agent</h1>
        <div class="meta">
          <span class="pill" id="version">version loading</span>
          <span class="pill" id="provider">provider loading</span>
        </div>
      </header>
      <section id="messages" aria-live="polite"></section>
      <form class="composer" id="form">
        <textarea id="input" placeholder="Ask an IT helpdesk question"></textarea>
        <button id="send" type="submit">Send</button>
      </form>
    </main>
    <aside>
      <div class="side-head">
        <h2>Tool Trace</h2>
        <div class="status" id="status">Starting session</div>
      </div>
      <section id="tools">
        <p class="empty">Tool calls will appear here with input arguments and results.</p>
      </section>
      <div class="footer" id="transcript">Transcript path loading</div>
    </aside>
  </div>
  <script>
    const state = {
      turns: [],
      transcriptPath: "",
      artifactVersion: "",
      provider: ""
    };

    const messagesEl = document.querySelector("#messages");
    const toolsEl = document.querySelector("#tools");
    const statusEl = document.querySelector("#status");
    const transcriptEl = document.querySelector("#transcript");
    const inputEl = document.querySelector("#input");
    const sendEl = document.querySelector("#send");
    const formEl = document.querySelector("#form");

    function jsonBlock(value) {
      return JSON.stringify(value, null, 2);
    }

    function renderMessages() {
      messagesEl.innerHTML = "";
      if (!state.turns.length) {
        const empty = document.createElement("p");
        empty.className = "empty";
        empty.textContent = "Start a helpdesk conversation. The transcript is saved after each turn.";
        messagesEl.appendChild(empty);
        return;
      }

      for (const turn of state.turns) {
        const user = document.createElement("article");
        user.className = "message user";
        user.innerHTML = `<span class="role">User</span>${escapeHtml(turn.user || "")}`;
        messagesEl.appendChild(user);

        const assistant = document.createElement("article");
        assistant.className = "message assistant";
        const text = turn.error ? `ERROR: ${turn.error}` : (turn.assistant_text || "");
        assistant.innerHTML = `<span class="role">Agent</span>${escapeHtml(text)}`;
        if (turn.error) assistant.classList.add("error");
        messagesEl.appendChild(assistant);
      }
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function renderTools() {
      const events = [];
      for (const turn of state.turns) {
        for (const event of turn.tool_events || []) {
          events.push({ turn: turn.turn_index, ...event });
        }
      }

      toolsEl.innerHTML = "";
      if (!events.length) {
        const empty = document.createElement("p");
        empty.className = "empty";
        empty.textContent = "No tools called yet.";
        toolsEl.appendChild(empty);
        return;
      }

      events.forEach((event, index) => {
        const item = document.createElement("article");
        item.className = "tool";
        const hasError = event.result && event.result.error;
        item.innerHTML = `
          <div class="tool-title">
            <span>${escapeHtml(event.tool || "unknown_tool")}</span>
            <span>turn ${event.turn} · #${index + 1}${hasError ? " · error" : ""}</span>
          </div>
          <details open>
            <summary>Input</summary>
            <pre>${escapeHtml(jsonBlock(event.args || {}))}</pre>
          </details>
          <details open>
            <summary>Result</summary>
            <pre>${escapeHtml(jsonBlock(event.result || {}))}</pre>
          </details>`;
        toolsEl.appendChild(item);
      });
    }

    function renderMeta() {
      document.querySelector("#version").textContent = state.artifactVersion || "version unknown";
      document.querySelector("#provider").textContent = state.provider || "provider unknown";
      transcriptEl.textContent = state.transcriptPath ? `Transcript: ${state.transcriptPath}` : "Transcript not created yet";
    }

    function render() {
      renderMeta();
      renderMessages();
      renderTools();
    }

    function escapeHtml(text) {
      return String(text)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function api(path, body) {
      const response = await fetch(path, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body || {})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || response.statusText);
      return data;
    }

    async function start() {
      const data = await api("/api/start", {});
      state.transcriptPath = data.transcript_path;
      state.artifactVersion = data.artifact_version;
      state.provider = `${data.provider}${data.model ? " / " + data.model : ""}`;
      state.turns = [];
      statusEl.textContent = "Ready";
      render();
      inputEl.focus();
    }

    formEl.addEventListener("submit", async (event) => {
      event.preventDefault();
      const text = inputEl.value.trim();
      if (!text) return;

      inputEl.value = "";
      sendEl.disabled = true;
      statusEl.textContent = "Running model and tools";
      state.turns.push({turn_index: state.turns.length + 1, user: text, assistant_text: "Working...", tool_events: []});
      render();

      try {
        const data = await api("/api/message", {message: text});
        Object.assign(state, {
          turns: data.turns,
          transcriptPath: data.transcript_path,
          artifactVersion: data.artifact_version,
          provider: `${data.provider}${data.model ? " / " + data.model : ""}`
        });
        statusEl.textContent = data.status || "Saved";
      } catch (error) {
        state.turns[state.turns.length - 1].assistant_text = String(error.message || error);
        statusEl.textContent = "Request failed";
      } finally {
        sendEl.disabled = false;
        render();
        inputEl.focus();
      }
    });

    start().catch((error) => {
      statusEl.textContent = "Startup failed";
      messagesEl.innerHTML = `<p class="empty error">${escapeHtml(error.message || error)}</p>`;
    });
  </script>
</body>
</html>
"""


class UISession:
    def __init__(
        self,
        *,
        provider_name: str,
        model: str | None,
        version: str,
        system_prompt_path: Path,
        tools_path: Path,
        transcripts_dir: Path,
        history_window: int,
        max_tool_rounds: int,
    ) -> None:
        load_lab_env(ROOT)
        self.provider_name = provider_name
        self.provider = make_provider(provider_name)
        self.model = model or getattr(self.provider, "default_model", None)
        self.version = version
        self.system_prompt_path = system_prompt_path
        self.tools_path = tools_path
        self.system_prompt = system_prompt_path.read_text(encoding="utf-8")
        declarations = load_tool_declarations(tools_path)
        self.tools = to_openai_tools(declarations)
        self.history_window = history_window
        self.max_tool_rounds = max_tool_rounds
        self.artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
        self.transcript_path = transcripts_dir / f"{transcript_id}.transcript.json"
        self.history: list[dict[str, str]] = []
        self.transcript: dict[str, Any] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(self.artifact_version),
            "provider": provider_name,
            "model": self.model,
            "system_prompt": str(system_prompt_path),
            "tools": str(tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "ui": "ui_server.py",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
        write_transcript(self.transcript_path, self.transcript)

    def snapshot(self) -> dict[str, Any]:
        return {
            "artifact_version": self.artifact_version.artifact_version,
            "provider": self.provider_name,
            "model": self.model,
            "transcript_path": str(self.transcript_path),
            "turns": self.transcript["turns"],
        }

    def send(self, user_text: str) -> dict[str, Any]:
        turn_index = len(self.transcript["turns"]) + 1
        turn_record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }

        messages = [
            {"role": "system", "content": self.system_prompt},
            *trim_history(self.history, self.history_window),
            {"role": "user", "content": user_text},
        ]

        try:
            result = run_model_tool_loop(
                provider=self.provider,
                messages=messages,
                tools=self.tools,
                model=self.model,
                max_tool_rounds=self.max_tool_rounds,
            )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": assistant_text})
        except Exception as exc:
            turn_record.update({
                "status": "provider_error",
                "error": f"{type(exc).__name__}: {exc}",
                "assistant_text": f"Provider error: {type(exc).__name__}: {exc}",
            })

        turn_record["ended_at"] = now_iso()
        self.transcript["turns"].append(turn_record)
        write_transcript(self.transcript_path, self.transcript)
        return self.snapshot() | {"status": turn_record["status"]}


def make_handler(session: UISession) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return

        def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2, default=str).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/":
                self.send_error(HTTPStatus.NOT_FOUND.value)
                return
            body = INDEX_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON body"}, HTTPStatus.BAD_REQUEST)
                return

            if parsed.path == "/api/start":
                self.send_json(session.snapshot())
                return

            if parsed.path == "/api/message":
                message = str(payload.get("message", "")).strip()
                if not message:
                    self.send_json({"error": "Message is required"}, HTTPStatus.BAD_REQUEST)
                    return
                self.send_json(session.send(message))
                return

            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a browser UI for the IT Helpdesk Agent.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--system-prompt", type=Path, default=ARTIFACTS_DIR / "system_prompt.md")
    parser.add_argument("--tools", type=Path, default=ARTIFACTS_DIR / "tools.yaml")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    args = parser.parse_args()

    session = UISession(
        provider_name=args.provider,
        model=args.model,
        version=args.version,
        system_prompt_path=args.system_prompt,
        tools_path=args.tools,
        transcripts_dir=args.transcripts_dir,
        history_window=args.history_window,
        max_tool_rounds=args.max_tool_rounds,
    )
    server = ThreadingHTTPServer((args.host, args.port), make_handler(session))
    url = f"http://{args.host}:{args.port}"
    print(f"Northstar Helpdesk Agent UI: {url}")
    print(f"Artifact version: {session.artifact_version.artifact_version}")
    print(f"Transcript: {session.transcript_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UI server.")


if __name__ == "__main__":
    main()
