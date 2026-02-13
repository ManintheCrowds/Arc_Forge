// PURPOSE: Idea Web bottom panel — graph from tags + [[wikilinks]].
// DEPENDENCIES: api.js, pipeline.js
// MODIFICATION NOTES: Phase 3 Idea Web.

import { get } from "./api.js";
import { renderMermaidInto } from "./pipeline.js";

function sanitizeId(s) {
  return String(s).replace(/[^a-zA-Z0-9_]/g, "_").slice(0, 30) || "n";
}

function nodesEdgesToMermaid(nodes, edges) {
  if (!nodes.length) return "";
  const idMap = {};
  const lines = [];
  nodes.forEach((n, i) => {
    const sid = sanitizeId(n.id) || "n" + i;
    idMap[n.id] = sid;
    const label = (n.label || n.id).replace(/"/g, "'");
    lines.push(`  ${sid}["${label}"]`);
  });
  edges.forEach((e) => {
    const fromId = idMap[e.from] || sanitizeId(e.from);
    const toId = idMap[e.to] || sanitizeId(e.to);
    if (fromId && toId && fromId !== toId) {
      lines.push(`  ${fromId} --> ${toId}`);
    }
  });
  return "flowchart LR\n" + lines.join("\n");
}

export function refreshIdeaWeb() {
  const el = document.getElementById("bottom-idea-web");
  if (!el) return;
  const campaign = (document.getElementById("module-campaign") || {}).value || "first_arc";
  const module = (document.getElementById("module-select") || {}).value || "default";
  el.innerHTML = "<p class=\"muted\">Loading…</p>";
  get("/api/workbench/idea-web?campaign=" + encodeURIComponent(campaign) + "&module=" + encodeURIComponent(module))
    .then((d) => {
      const nodes = (d && d.nodes) || [];
      const edges = (d && d.edges) || [];
      if (nodes.length === 0) {
        el.innerHTML = "<p class=\"muted\">No links or tags found. Add <code>tags</code> or <code>[[wikilinks]]</code> to notes.</p>";
        return;
      }
      const mermaid = nodesEdgesToMermaid(nodes, edges);
      el.innerHTML = "";
      renderMermaidInto(el, mermaid, "No graph data.");
    })
    .catch(() => {
      el.innerHTML = "<p class=\"muted err\">Failed to load idea web.</p>";
    });
}
