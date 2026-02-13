// PURPOSE: workflow_ui entry point; wires modules together.
// DEPENDENCIES: modules/*
// MODIFICATION NOTES: Wave C modularization.

import { get } from "./modules/api.js";
import { formatErr } from "./modules/utils.js";
import { initModalHandlers } from "./modules/modal.js";
import { initKbHandlers, refreshKbStatus } from "./modules/kb.js";
import { initSessionHandlers, refreshSessionMemoryFiles } from "./modules/session.js";
import { initTaskDecompHandlers, initFeedbackHandlers, refreshTaskDecompForm, refreshFeedbackForm, refreshS4Drafts, isTdDirty, isFbDirty } from "./modules/forms.js";
import { refreshTree, viewFile } from "./modules/files.js";
import { renderPipelineMermaid, refreshArtifacts, setAutoRefresh } from "./modules/pipeline.js";
import { getArcId, setArcId } from "./modules/state.js";
import { escapeHtml } from "./modules/utils.js";
import { refreshPrereqs } from "./modules/prereqs.js";
import { initStageHandlers } from "./modules/stages.js";
import { initWizard, checkFirstRunOverlay } from "./modules/wizard.js";
import { initWorkbenchModuleSelector } from "./modules/workbench.js";
import { initNoteEditor } from "./modules/note_editor.js";
import { initWorkflow } from "./modules/workflow.js";
import { refreshIdeaWeb } from "./modules/idea_web.js";
import { refreshDependencies } from "./modules/dependencies.js";
import { initChat } from "./modules/chat.js";

function showTab(name) {
  const current = document.querySelector(".tabs button.active");
  const currentTab = current ? current.dataset.tab : "";
  if (currentTab === "form1" && isTdDirty() && name !== "form1") {
    if (!confirm("Task decomposition has unsaved changes. Leave?")) return;
  }
  if (currentTab === "form3" && isFbDirty() && name !== "form3") {
    if (!confirm("Feedback has unsaved changes. Leave?")) return;
  }
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".stage-panel").forEach((p) => p.classList.toggle("visible", p.id === "panel-" + name));
  if (name === "session-memory") refreshSessionMemoryFiles();
  if (name === "kb") refreshKbStatus();
}

function refreshArcs() {
  get("/api/arcs").then((d) => {
    const sel = document.getElementById("arc-select");
    if (!sel) return;
    const arcs = d.arcs || [];
    sel.innerHTML = arcs.map((a) => `<option value="${a}">${a}</option>`).join("");
    if (!arcs.length) {
      sel.innerHTML = "<option value=\"first_arc\">first_arc</option>";
    }
    sel.value = getArcId();
    sel.onchange = function () {
      setArcId(sel.value);
      refreshTree();
      refreshArtifacts(getArcId());
      refreshTaskDecompForm();
      refreshFeedbackForm();
      refreshS4Drafts();
      refreshTimeline();
      const toggle = document.getElementById("auto-refresh-toggle");
      if (toggle && toggle.checked) {
        setAutoRefresh(true, getArcId(), refreshTree);
      }
    };
  }).catch(() => {});
}

function initAutoRefreshToggle() {
  const toggle = document.getElementById("auto-refresh-toggle");
  if (!toggle) return;
  toggle.addEventListener("change", () => {
    setAutoRefresh(toggle.checked, getArcId(), refreshTree);
  });
}

function showWorkspace(name) {
  document.querySelectorAll(".workspace-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.workspace === name));
  document.querySelectorAll(".workspace-view").forEach((v) => v.classList.toggle("visible", v.id === "workspace-" + name));
  if (name === "legacy") checkFirstRunOverlay();
}

function initWorkspaceTabs() {
  document.querySelectorAll(".workspace-tabs button").forEach((b) => {
    b.addEventListener("click", () => showWorkspace(b.dataset.workspace));
  });
}


function showRightPanel(name) {
  document.querySelectorAll(".right-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.right === name));
  document.querySelectorAll(".right-panel").forEach((p) => p.classList.toggle("visible", p.id === "right-" + name));
}

function initRightTabs() {
  document.querySelectorAll(".right-tabs button").forEach((b) => {
    b.addEventListener("click", () => showRightPanel(b.dataset.right));
  });
}

function showBottomPanel(name) {
  document.querySelectorAll(".bottom-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.bottom === name));
  document.querySelectorAll(".bottom-panel").forEach((p) => p.classList.toggle("visible", p.id === "bottom-" + name));
  if (name === "timeline") refreshTimeline();
  if (name === "idea-web") refreshIdeaWeb();
  if (name === "dependencies") refreshDependencies();
}

function refreshTimeline() {
  const el = document.getElementById("bottom-timeline");
  if (!el) return;
  const campaign = getArcId();
  get("/api/workbench/timeline?campaign=" + encodeURIComponent(campaign)).then((d) => {
    const items = (d && d.items) || [];
    if (items.length === 0) {
      el.innerHTML = "<p class=\"muted\">No dated notes. Add <code>date</code>, <code>session_date</code>, or <code>timeline_order</code> to frontmatter in Campaigns/" + escapeHtml(campaign) + "/ or _session_memory/.</p>";
      return;
    }
    el.innerHTML = "<ul class=\"timeline-list\">" + items.map((it) => {
      const subpath = it.path.startsWith(campaign + "/") ? it.path.slice(campaign.length + 1) : it.path.startsWith("_session_memory/") ? it.path : it.path;
      const isSession = it.path.startsWith("_session_memory/");
      const display = "<span class=\"timeline-date\">" + escapeHtml(it.date) + "</span> <span class=\"timeline-type\">[" + escapeHtml(it.type) + "]</span> <a href=\"#\" class=\"timeline-link\" data-path=\"" + escapeHtml(it.path) + "\" data-subpath=\"" + escapeHtml(subpath) + "\" data-session=\"" + (isSession ? "1" : "0") + "\">" + escapeHtml(it.title) + "</a>";
      return "<li>" + display + "</li>";
    }).join("") + "</ul>";
    el.querySelectorAll(".timeline-link").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        const subpath = a.getAttribute("data-subpath");
        const isSession = a.getAttribute("data-session") === "1";
        if (isSession && subpath) {
          const fname = subpath.replace(/^.*\//, "");
          fetch("/api/session/file/" + encodeURIComponent(fname))
            .then((r) => (r.ok ? r.text() : Promise.reject(new Error(r.status + " " + r.statusText))))
            .then((t) => {
              import("./modules/modal.js").then(({ showFileModal }) => showFileModal(subpath, t, "", false));
            })
            .catch((err) => {
              import("./modules/modal.js").then(({ showFileModal }) => showFileModal("Error", formatErr(err), "", true));
            });
        } else {
          viewFile(subpath);
        }
      });
    });
  }).catch((e) => {
    el.innerHTML = "<p class=\"muted err\">Timeline load failed: " + escapeHtml(formatErr(e)) + "</p>";
  });
}

function initBottomTabs() {
  document.querySelectorAll(".bottom-tabs button").forEach((b) => {
    b.addEventListener("click", () => showBottomPanel(b.dataset.bottom));
  });
}

function initRagSearch() {
  const btn = document.getElementById("rag-search");
  const input = document.getElementById("rag-query");
  const results = document.getElementById("rag-results");
  if (!btn || !results) return;
  btn.addEventListener("click", function () {
    const query = (input && input.value || "").trim();
    if (!query) {
      results.innerHTML = "";
      const pre = document.createElement("pre");
      pre.className = "err";
      pre.textContent = "Enter a search query.";
      results.appendChild(pre);
      return;
    }
    btn.disabled = true;
    results.innerHTML = "";
    const pre = document.createElement("pre");
    pre.textContent = "Searching…";
    results.appendChild(pre);
    get("/api/kb/search?query=" + encodeURIComponent(query) + "&limit=20").then((d) => {
      results.innerHTML = "";
      const out = document.createElement("pre");
      out.className = "ok";
      out.textContent = typeof d === "string" ? d : JSON.stringify(d, null, 2);
      if (d && d.results && d.results.length === 0) {
        out.textContent = (d.query ? "No results for: " + d.query : JSON.stringify(d, null, 2));
      }
      results.appendChild(out);
    }).catch((e) => {
      results.innerHTML = "";
      const err = document.createElement("pre");
      err.className = "err";
      err.textContent = formatErr(e);
      results.appendChild(err);
    }).finally(() => { btn.disabled = false; });
  });
}

initModalHandlers();
initWorkspaceTabs();
initChat();
initRightTabs();
initBottomTabs();
initWorkbenchModuleSelector();
initNoteEditor();
initWorkflow();
initRagSearch();
initKbHandlers();
initSessionHandlers();
initTaskDecompHandlers();
initFeedbackHandlers();
initStageHandlers();
initWizard(showTab);
initAutoRefreshToggle();

document.querySelectorAll(".tabs button").forEach((b) => {
  b.addEventListener("click", () => showTab(b.dataset.tab));
});

window.addEventListener("beforeunload", (e) => {
  if (isTdDirty() || isFbDirty()) e.preventDefault();
});

refreshArcs();
refreshTree();
refreshArtifacts(getArcId());
checkFirstRunOverlay();
refreshTaskDecompForm();
refreshFeedbackForm();
refreshS4Drafts();
showTab("s1");
renderPipelineMermaid();
refreshPrereqs();
refreshTimeline();
