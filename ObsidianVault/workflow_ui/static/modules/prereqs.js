// PURPOSE: Prerequisites status panel logic.
// DEPENDENCIES: api.js
// MODIFICATION NOTES: Extracted from app.js.

import { get } from "./api.js";

function setStatusBadge(id, ok, text) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  el.classList.toggle("ok", !!ok);
  el.classList.toggle("err", !ok);
}

export function refreshPrereqs() {
  get("/api/status").then((d) => {
    setStatusBadge("status-campaigns", d.campaigns && d.campaigns.ok, d.campaigns && d.campaigns.ok ? "OK" : "Missing");
    setStatusBadge("status-config", d.config && d.config.ok, d.config && d.config.ok ? "OK" : "Missing");
    setStatusBadge("status-kb", d.campaign_kb && d.campaign_kb.ok, d.campaign_kb && d.campaign_kb.ok ? "OK" : "Unavailable");
  }).catch(() => {
    setStatusBadge("status-campaigns", false, "Unknown");
    setStatusBadge("status-config", false, "Unknown");
    setStatusBadge("status-kb", false, "Unknown");
  });
}
