// PURPOSE: Optional guided wizard for S1–S5.
// DEPENDENCIES: none
// MODIFICATION NOTES: New Wave C feature.

const steps = [
  { id: "s1", title: "S1 Task Decomp", hint: "Requires storyboard under Campaigns/_rag_outputs/." },
  { id: "s2", title: "S2 Drafts", hint: "Requires task_decomposition and storyboard; runs RAG." },
  { id: "s3", title: "S3 Feedback", hint: "Human-only: edit feedback in the form." },
  { id: "s4", title: "S4 Refine", hint: "Pick a draft and feedback file." },
  { id: "s5", title: "S5 Export", hint: "Exports expanded storyboard, JSON, campaign_kb file." },
];

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
}
