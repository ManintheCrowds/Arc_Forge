// PURPOSE: workflow_ui entry point; wires modules together.
// DEPENDENCIES: modules/*
// MODIFICATION NOTES: Wave C modularization.

import { get } from "./modules/api.js";
import { initModalHandlers } from "./modules/modal.js";
import { initKbHandlers, refreshKbStatus } from "./modules/kb.js";
import { initSessionHandlers, refreshSessionMemoryFiles } from "./modules/session.js";
import { initTaskDecompHandlers, initFeedbackHandlers, refreshTaskDecompForm, refreshFeedbackForm, refreshS4Drafts, isTdDirty, isFbDirty } from "./modules/forms.js";
import { refreshTree } from "./modules/files.js";
import { renderPipelineMermaid, refreshArtifacts, setAutoRefresh } from "./modules/pipeline.js";
import { getArcId, setArcId } from "./modules/state.js";
import { refreshPrereqs } from "./modules/prereqs.js";
import { initStageHandlers } from "./modules/stages.js";
import { initWizard } from "./modules/wizard.js";

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

initModalHandlers();
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
refreshTaskDecompForm();
refreshFeedbackForm();
refreshS4Drafts();
showTab("s1");
renderPipelineMermaid();
refreshPrereqs();
