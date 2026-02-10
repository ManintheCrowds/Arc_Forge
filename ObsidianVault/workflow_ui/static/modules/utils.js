// PURPOSE: Shared utility helpers.
// DEPENDENCIES: none
// MODIFICATION NOTES: Extracted from monolithic app.js (Wave C modularization).

export function formatErr(e) {
  if (!e) return "Unknown error";
  if (typeof e === "string") return e;
  return e.error || e.reason || e.detail || e.message || JSON.stringify(e);
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
  el.textContent = errors.join("\n");
  el.classList.add("visible");
}
