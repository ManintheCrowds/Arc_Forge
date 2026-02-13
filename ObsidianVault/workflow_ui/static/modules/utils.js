// PURPOSE: Shared utility helpers.
// DEPENDENCIES: none
// MODIFICATION NOTES: Extracted from monolithic app.js (Wave C modularization).

/** Actionable hints for generic stage errors (UW-3). */
const _STAGE_HINTS = {
  stage1_failed: "Ensure a storyboard exists under Campaigns/_rag_outputs/ (or pass storyboard_path).",
  stage2_failed: "Run S1 first to generate task_decomposition.yaml. Ensure storyboard exists under Campaigns/_rag_outputs/.",
  stage4_failed: "Run S2 to generate drafts, then S3 to add feedback and save. Ensure {arc}_feedback.yaml exists.",
  stage5_failed: "Run S1–S4 first. Ensure encounter drafts exist under encounters/.",
};

export function formatErr(e) {
  if (!e) return "Unknown error";
  if (typeof e === "string") return e;
  const msg = (e && (e.detail || e.error || e.reason || e.message)) || String(e);
  if (msg === "[object Object]") return "Unknown error";
  const errKey = (e && (e.error || e.reason || "")) + "";
  const hint = _STAGE_HINTS[errKey];
  if (hint) {
    return msg === errKey ? `${msg}. ${hint}` : `${msg}\n\nHint: ${hint}`;
  }
  return msg;
}

export function escapeHtml(s) {
  if (s == null) return "";
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

export function setProgress(id, active) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle("active", !!active);
}

export function setValidationErrors(id, errors) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!errors || errors.length === 0) {
    el.textContent = "";
    el.classList.remove("visible");
    return;
  }
  el.innerHTML = errors.map((e) => `<div class="validation-item">${escapeHtml(e)}</div>`).join("");
  el.classList.add("visible");
}
