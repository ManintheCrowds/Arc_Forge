// PURPOSE: Session memory (Archivist / Foreshadow) logic.
// DEPENDENCIES: api.js, utils.js
// MODIFICATION NOTES: Extracted from app.js.

import { get, post } from "./api.js";
import { escapeHtml, formatErr, setProgress } from "./utils.js";

export function refreshSessionMemoryFiles() {
  return get("/api/session/files").then((d) => {
    const files = d.files || [];
    const optionsHtml = "<option value=\"\">(pick from _session_memory or type below)</option>" +
      files.map((f) => `<option value="${escapeHtml(f.path)}">${escapeHtml(f.name)}</option>`).join("");
    const foreshadowSel = document.getElementById("session-foreshadow-dropdown");
    if (foreshadowSel) {
      foreshadowSel.innerHTML = optionsHtml;
      foreshadowSel.onchange = function () {
        const input = document.getElementById("session-foreshadow-path");
        if (input) input.value = foreshadowSel.value || "";
      };
    }
    const archivistSel = document.getElementById("session-archivist-dropdown");
    if (archivistSel) {
      archivistSel.innerHTML = optionsHtml;
      archivistSel.onchange = function () {
        const input = document.getElementById("session-archivist-path");
        if (input) input.value = archivistSel.value || "";
      };
    }
  }).catch(() => {});
}

function outSessionMemory(data, isErr) {
  const el = document.getElementById("out-session-memory");
  if (!el) return;
  el.innerHTML = "";
  const isError = isErr || (data && data.status === "error");
  const isSkipped = !isError && data && data.status === "skipped";
  let statusClass = "ok";
  if (isError) statusClass = "err";
  else if (isSkipped) statusClass = "warn";
  if (isSkipped && data.reason) {
    const line = document.createElement("p");
    line.className = "warn";
    line.textContent = "Skipped: " + data.reason;
    el.appendChild(line);
  }
  const pre = document.createElement("pre");
  pre.className = statusClass;
  pre.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  el.appendChild(pre);
  if (!isError && data && data.output_path) {
    const row = document.createElement("p");
    row.className = "muted";
    row.style.marginTop = "0.5em";
    row.appendChild(document.createTextNode("Output: " + data.output_path + " "));
    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "list-actions";
    copyBtn.textContent = "Copy path";
    copyBtn.style.marginLeft = "0.5em";
    copyBtn.onclick = function () {
      navigator.clipboard.writeText(data.output_path).then(() => {
        copyBtn.textContent = "Copied";
        setTimeout(() => { copyBtn.textContent = "Copy path"; }, 1500);
      }).catch(() => {});
    };
    row.appendChild(copyBtn);
    const filename = data.output_path.replace(/\\/g, "/").split("/").pop();
    if (filename && data.output_path.indexOf("_session_memory") !== -1) {
      const viewLink = document.createElement("a");
      viewLink.href = "/api/session/file/" + encodeURIComponent(filename);
      viewLink.target = "_blank";
      viewLink.rel = "noopener";
      viewLink.textContent = "View output";
      viewLink.style.marginLeft = "0.5em";
      row.appendChild(viewLink);
    }
    el.appendChild(row);
  }
}

export function initSessionHandlers() {
  document.getElementById("run-archivist").addEventListener("click", function () {
    const sessionPath = document.getElementById("session-archivist-path").value.trim();
    if (!sessionPath) { outSessionMemory("Enter a session note path.", true); return; }
    this.disabled = true;
    setProgress("progress-session", true);
    const outEl = document.getElementById("out-session-memory");
    if (outEl) outEl.innerHTML = "<p class=\"muted\">Running…</p>";
    post("/api/session/archivist", { session_path: sessionPath })
      .then((r) => {
        outSessionMemory(r);
        if (r && r.status === "success" && r.output_path) {
          const foreshadowInput = document.getElementById("session-foreshadow-path");
          if (foreshadowInput) foreshadowInput.value = r.output_path;
        }
      })
      .catch((e) => outSessionMemory(formatErr(e), true))
      .finally(() => { this.disabled = false; setProgress("progress-session", false); });
  });

  document.getElementById("run-foreshadow").addEventListener("click", function () {
    const contextPath = document.getElementById("session-foreshadow-path").value.trim();
    if (!contextPath) { outSessionMemory("Enter a context file path (Archivist output or session summary).", true); return; }
    this.disabled = true;
    setProgress("progress-session", true);
    const outEl = document.getElementById("out-session-memory");
    if (outEl) outEl.innerHTML = "<p class=\"muted\">Running…</p>";
    post("/api/session/foreshadow", { context_path: contextPath })
      .then((r) => outSessionMemory(r))
      .catch((e) => outSessionMemory(formatErr(e), true))
      .finally(() => { this.disabled = false; setProgress("progress-session", false); });
  });
}
