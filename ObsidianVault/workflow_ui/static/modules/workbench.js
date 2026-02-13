// PURPOSE: Workbench module selector (campaigns, modules, tree + create module).
// DEPENDENCIES: api.js, utils.js
// MODIFICATION NOTES: Phase 2 module selector; Phase 3 create module.

import { get, post } from "./api.js";
import { escapeHtml, formatErr } from "./utils.js";

let _campaign = "";
let _module = "";

export function initWorkbenchModuleSelector() {
  const campaignSel = document.getElementById("module-campaign");
  const moduleSel = document.getElementById("module-select");
  const treeEl = document.getElementById("module-tree");
  const filterType = document.getElementById("filter-type");
  const filterStatus = document.getElementById("filter-status");

  if (!campaignSel || !moduleSel || !treeEl) return;

  function refreshModules() {
    const camp = campaignSel.value || "first_arc";
    _campaign = camp;
    moduleSel.innerHTML = "<option value=\"\">(loading…)</option>";
    get("/api/workbench/modules?campaign=" + encodeURIComponent(camp)).then((d) => {
      const mods = (d && d.modules) || ["default"];
      moduleSel.innerHTML = mods.map((m) => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
      _module = moduleSel.value || (mods[0] || "default");
      refreshTree();
    }).catch(() => {
      moduleSel.innerHTML = "<option value=\"default\">default</option>";
      refreshTree();
    });
  }

  function refreshTree() {
    const camp = campaignSel.value || _campaign || "first_arc";
    const mod = moduleSel.value || _module || "default";
    const typeVal = filterType && filterType.value ? filterType.value : "";
    const statusVal = filterStatus && filterStatus.value ? filterStatus.value : "";
    const params = new URLSearchParams({ campaign: camp, module: mod });
    if (typeVal) params.set("type", typeVal);
    if (statusVal) params.set("status", statusVal);
    treeEl.innerHTML = "<p class=\"muted\">Loading…</p>";
    get("/api/workbench/tree?" + params.toString()).then((d) => {
      const nodes = (d && d.nodes) || [];
      if (nodes.length === 0) {
        treeEl.innerHTML = "<p class=\"muted\">No notes with frontmatter.</p>";
        return;
      }
      treeEl.innerHTML = "<ul class=\"module-tree-list\">" + nodes.map((n) =>
        "<li class=\"tree-node\" data-path=\"" + escapeHtml(n.path || "") + "\" role=\"button\" tabindex=\"0\"><span class=\"tree-type\">[" + escapeHtml(n.type) + "]</span> " + escapeHtml(n.name) + "</li>"
      ).join("") + "</ul>";
      treeEl.querySelectorAll(".tree-node[data-path]").forEach((li) => {
        li.addEventListener("click", () => {
          const path = li.getAttribute("data-path");
          if (path) window.dispatchEvent(new CustomEvent("workbench:tree-select", { detail: { path } }));
        });
      });
    }).catch(() => {
      treeEl.innerHTML = "<p class=\"muted\">Failed to load tree.</p>";
    });
  }

  get("/api/workbench/campaigns").then((d) => {
    const camps = (d && d.campaigns) || [];
    campaignSel.innerHTML = camps.length ? camps.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("") : "<option value=\"first_arc\">first_arc</option>";
    _campaign = campaignSel.value || (camps[0] || "first_arc");
    refreshModules();
  }).catch(() => {
    campaignSel.innerHTML = "<option value=\"first_arc\">first_arc</option>";
    refreshModules();
  });

  campaignSel.addEventListener("change", refreshModules);
  moduleSel.addEventListener("change", refreshTree);
  if (filterType) filterType.addEventListener("change", refreshTree);
  if (filterStatus) filterStatus.addEventListener("change", refreshTree);
  window.addEventListener("workbench:refresh", refreshTree);

  const createBtn = document.getElementById("create-module-btn");
  const createOut = document.getElementById("create-module-out");
  if (createBtn && createOut) {
    createBtn.addEventListener("click", () => {
      const camp = (document.getElementById("create-campaign") || {}).value?.trim() || "";
      const mod = (document.getElementById("create-module") || {}).value?.trim() || "";
      if (!camp || !mod) {
        createOut.textContent = "Enter campaign and module name.";
        createOut.className = "out err";
        return;
      }
      const scenes = parseInt((document.getElementById("create-scenes") || {}).value || "1", 10) || 1;
      const npcs = parseInt((document.getElementById("create-npcs") || {}).value || "1", 10) || 1;
      createBtn.disabled = true;
      createOut.textContent = "Creating…";
      post("/api/workbench/create-module", { campaign: camp, module: mod, starting_scenes: scenes, starting_npcs: npcs })
        .then((d) => {
          createOut.textContent = "Created: " + (d.path || d.status || "OK");
          createOut.className = "out ok";
          refreshModules();
        })
        .catch((e) => {
          createOut.textContent = "Failed: " + formatErr(e);
          createOut.className = "out err";
        })
        .finally(() => { createBtn.disabled = false; });
    });
  }
}
