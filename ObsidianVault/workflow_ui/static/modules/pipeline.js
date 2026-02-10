// PURPOSE: Pipeline badges, mermaid rendering, and live updates.
// DEPENDENCIES: api.js, state.js, utils.js
// MODIFICATION NOTES: Extracted from app.js; added optional polling.

import { get } from "./api.js";
import { setArtifacts } from "./state.js";
import { setProgress } from "./utils.js";

let autoRefreshTimer = null;

export function refreshArtifacts(arcId) {
  return get("/api/arc/" + encodeURIComponent(arcId) + "/artifacts").then((d) => {
    setArtifacts(d);
    const badges = document.getElementById("pipeline-badges");
    if (badges) {
      const stages = [
        { key: "Storyboard", has: true },
        { key: "S1", has: d.task_decomposition },
        { key: "S2", has: d.has_encounters || d.has_opportunities },
        { key: "S3", has: d.feedback },
        { key: "S4", has: d.has_encounters },
        { key: "S5", has: d.expanded_storyboard && d.encounters_json },
      ];
      badges.innerHTML = stages.map((s, i) => {
        const cls = s.has ? "stage has-art" : "stage";
        const arr = i < stages.length - 1 ? "<span class=\"arrow\">→</span>" : "";
        return `<span class="${cls}">${s.key}</span>${arr}`;
      }).join("");
    }
  }).catch(() => {});
}

export function renderMermaidInto(container, mermaidText, fallbackText) {
  if (!container) return;
  container.innerHTML = "";
  container.classList.remove("mermaid-fallback");
  if (!mermaidText) {
    if (fallbackText) {
      container.textContent = fallbackText;
      container.classList.add("mermaid-fallback");
    }
    return;
  }
  const wrap = document.createElement("div");
  wrap.className = "mermaid";
  wrap.textContent = mermaidText;
  container.appendChild(wrap);
  if (window.mermaid && window.mermaid.run) {
    window.mermaid.run({ nodes: [wrap] }).catch(() => {
      if (!fallbackText) return;
      container.innerHTML = "";
      container.textContent = fallbackText;
      container.classList.add("mermaid-fallback");
    });
  } else if (fallbackText) {
    container.innerHTML = "";
    container.textContent = fallbackText;
    container.classList.add("mermaid-fallback");
  }
}

export function renderPipelineMermaid() {
  return get("/api/diagrams/pipeline_mermaid").then((d) => {
    const mermaidText = d && d.mermaid ? d.mermaid : "";
    renderMermaidInto(document.getElementById("pipeline-strip-mermaid"), mermaidText, "");
    renderMermaidInto(document.getElementById("pipeline-mermaid"), mermaidText, "No diagram available.");
  }).catch(() => {});
}

export function setAutoRefresh(enabled, arcId, refreshTreeFn) {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer);
    autoRefreshTimer = null;
  }
  if (!enabled) return;
  autoRefreshTimer = setInterval(() => {
    setProgress("progress-auto-refresh", true);
    Promise.all([
      refreshArtifacts(arcId),
      refreshTreeFn ? refreshTreeFn() : Promise.resolve(),
    ]).finally(() => setProgress("progress-auto-refresh", false));
  }, 10000);
}
