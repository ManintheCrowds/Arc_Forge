// PURPOSE: Workbench Chat — POST to /api/workbench/chat, append messages.
// DEPENDENCIES: api.js, utils.js
// MODIFICATION NOTES: Phase 3 Chat. AI security P2: kill switch (Stop button).

import { post } from "./api.js";
import { formatErr } from "./utils.js";

function appendMessage(history, role, text, isErr) {
  if (!history) return;
  const div = document.createElement("div");
  div.className = "chat-msg " + (role === "user" ? "chat-user" : "chat-assistant") + (isErr ? " err" : "");
  const label = document.createElement("strong");
  label.textContent = role === "user" ? "You: " : "Assistant: ";
  div.appendChild(label);
  const pre = document.createElement("pre");
  pre.style.margin = "0.25rem 0 0";
  pre.style.whiteSpace = "pre-wrap";
  pre.textContent = text;
  div.appendChild(pre);
  history.appendChild(div);
  history.scrollTop = history.scrollHeight;
}

export function initChat() {
  const sendBtn = document.getElementById("chat-send");
  const stopBtn = document.getElementById("chat-stop");
  const input = document.getElementById("chat-input");
  const history = document.getElementById("chat-history");
  if (!sendBtn || !history) return;

  let abortController = null;

  sendBtn.addEventListener("click", () => {
    const text = (input && input.value || "").trim();
    if (!text) return;
    const contextPath = document.body.getAttribute("data-active-note-path") || "";
    if (input) input.value = "";
    appendMessage(history, "user", text);
    sendBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = false;
    abortController = new AbortController();
    post("/api/workbench/chat", { message: text, context_path: contextPath || undefined }, { signal: abortController.signal })
      .then((d) => {
        const reply = (d && d.reply) || (d && d.error) || "No response.";
        appendMessage(history, "assistant", reply, !!d.error);
      })
      .catch((e) => {
        if (e && e.name === "AbortError") {
          appendMessage(history, "assistant", "Stopped.", true);
        } else {
          appendMessage(history, "assistant", formatErr(e), true);
        }
      })
      .finally(() => {
        sendBtn.disabled = false;
        if (stopBtn) stopBtn.disabled = true;
        abortController = null;
      });
  });

  if (stopBtn) {
    stopBtn.addEventListener("click", () => {
      if (abortController) {
        abortController.abort();
      }
    });
  }
}
