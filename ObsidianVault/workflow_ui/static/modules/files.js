// PURPOSE: Arc tree + file viewer.
// DEPENDENCIES: api.js, modal.js, utils.js, state.js
// MODIFICATION NOTES: Extracted from app.js.

import { get } from "./api.js";
import { showFileModal } from "./modal.js";
import { escapeHtml, formatErr } from "./utils.js";
import { getArcId } from "./state.js";

function notFoundHint(relPath) {
  const p = relPath.replace(/\\/g, "/");
  if (p.includes("encounters") || p.includes("opportunities")) return "Run S2 to generate drafts.";
  if (p.includes("task_decomposition")) return "Run S1 first to generate task_decomposition.yaml.";
  if (p.includes("feedback") || p.includes("_feedback")) return "Edit Feedback (S3) and save feedback.yaml first.";
  return "";
}

export function viewFile(relPath) {
  const arcId = getArcId();
  const url = "/api/arc/" + encodeURIComponent(arcId) + "/file/" + encodeURIComponent(relPath.replace(/\\/g, "/"));
  fetch(url).then((r) => {
    if (!r.ok) {
      const hint = notFoundHint(relPath);
      return r.json().then((j) => {
        showFileModal("Not found", formatErr(j) || relPath, hint, true);
      }).catch(() => showFileModal("Not found", relPath, hint, true));
      return;
    }
    return r.text().then((text) => {
      const maxLen = 50000;
      const truncated = text.length > maxLen;
      const display = truncated ? text.slice(0, maxLen) + "\n… (truncated)" : text;
      const note = truncated ? "Note: file content truncated for display." : "";
      showFileModal(relPath, display, note, false);
    });
  }).catch((e) => showFileModal("Error", formatErr(e), "", true));
}

export function refreshTree() {
  const arcId = getArcId();
  return get("/api/arc/" + encodeURIComponent(arcId) + "/tree").then((d) => {
    const treeEl = document.getElementById("arc-tree");
    const files = (d.files || []).map((f) => `<li class="file">${f.name}</li>`).join("");
    treeEl.innerHTML = files || "<li class=\"file\">(no files)</li>";

    const encList = document.getElementById("encounters-list");
    const enc = (d.encounters || []).concat(d.opportunities || []).map((e) => {
      const prov = [];
      if (e.version) prov.push(e.version);
      if (e.source) prov.push("from " + e.source);
      const rel = e.rel || e.path;
      return `<div><a href="#" data-rel="${escapeHtml(rel)}">${escapeHtml(e.name)}</a><div class="provenance">${prov.map((p) => `<span>${escapeHtml(p)}</span>`).join("")}</div></div>`;
    }).join("");
    encList.innerHTML = enc || "<div class=\"muted\">(no encounters yet)</div>";
    encList.querySelectorAll("a[data-rel]").forEach((a) => {
      a.onclick = (ev) => {
        ev.preventDefault();
        viewFile(a.getAttribute("data-rel"));
      };
    });
  }).catch(() => {});
}
