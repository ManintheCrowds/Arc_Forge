// PURPOSE: Optional guided wizard for S1–S5; UW-10 first-run overlay for empty tree.
// DEPENDENCIES: api.js
// MODIFICATION NOTES: UW-10 first-run flow.

import { get } from "./api.js";

const FIRST_RUN_DISMISSED_KEY = "workflow_ui:first_run_dismissed";

const steps = [
  { id: "s1", title: "S1 Task Decomp", hint: "Requires storyboard under Campaigns/_rag_outputs/." },
  { id: "s2", title: "S2 Drafts", hint: "Requires task_decomposition and storyboard; runs RAG." },
  { id: "s3", title: "S3 Feedback", hint: "Human-only: edit feedback in the form." },
  { id: "s4", title: "S4 Refine", hint: "Pick a draft and feedback file." },
  { id: "s5", title: "S5 Export", hint: "Exports expanded storyboard, JSON, campaign_kb file." },
];

function isTreeEmpty(arcs, tree) {
  if (!arcs || arcs.length === 0) return true;
  const files = (tree && tree.files) || [];
  const encounters = (tree && tree.encounters) || [];
  const opportunities = (tree && tree.opportunities) || [];
  return files.length === 0 && encounters.length === 0 && opportunities.length === 0;
}

export function checkFirstRunOverlay() {
  const overlay = document.getElementById("first-run-overlay");
  const dismissCheck = document.getElementById("first-run-dismiss");
  if (!overlay || !dismissCheck) return;
  if (localStorage.getItem(FIRST_RUN_DISMISSED_KEY) === "1") {
    overlay.classList.remove("visible");
    return;
  }
  get("/api/arcs").then((d) => {
    const arcs = (d && d.arcs) || [];
    const arcId = arcs[0] || "first_arc";
    return get("/api/arc/" + encodeURIComponent(arcId) + "/tree").then((tree) => {
      if (isTreeEmpty(arcs, tree)) {
        overlay.classList.add("visible");
      } else {
        overlay.classList.remove("visible");
      }
    });
  }).catch(() => {
    overlay.classList.add("visible");
  });
}

export function initWizard(showTab) {
  const toggle = document.getElementById("wizard-toggle");
  const panel = document.getElementById("wizard-panel");
  const title = document.getElementById("wizard-title");
  const hint = document.getElementById("wizard-hint");
  const prev = document.getElementById("wizard-prev");
  const next = document.getElementById("wizard-next");
  const go = document.getElementById("wizard-go");
  if (!toggle || !panel || !title || !hint || !prev || !next || !go) return;

  let idx = 0;
  const render = () => {
    const step = steps[idx];
    title.textContent = step.title;
    hint.textContent = step.hint;
    prev.disabled = idx === 0;
    next.disabled = idx === steps.length - 1;
  };

  toggle.addEventListener("change", () => {
    panel.classList.toggle("visible", toggle.checked);
  });
  prev.addEventListener("click", () => { if (idx > 0) { idx -= 1; render(); } });
  next.addEventListener("click", () => { if (idx < steps.length - 1) { idx += 1; render(); } });
  go.addEventListener("click", () => {
    const step = steps[idx];
    showTab(step.id);
  });

  render();

  const overlay = document.getElementById("first-run-overlay");
  const dismissCheck = document.getElementById("first-run-dismiss");
  if (overlay && dismissCheck) {
    dismissCheck.addEventListener("change", () => {
      if (dismissCheck.checked) {
        localStorage.setItem(FIRST_RUN_DISMISSED_KEY, "1");
        overlay.classList.remove("visible");
      }
    });
  }
}
