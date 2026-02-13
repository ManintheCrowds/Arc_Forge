// PURPOSE: Task decomposition + feedback forms.
// DEPENDENCIES: api.js, validation.js, drafts.js, utils.js, state.js, modal.js
// MODIFICATION NOTES: Extracted from app.js.

import { get, put } from "./api.js";
import { validateTaskDecomp, validateFeedback, ENCOUNTER_TYPES, FEEDBACK_TYPES } from "./validation.js";
import { loadLocalDraft, saveLocalDraft, clearLocalDraft } from "./drafts.js";
import { escapeHtml, setValidationErrors } from "./utils.js";
import { getArcId } from "./state.js";
import { showFileModal } from "./modal.js";
import { formatErr } from "./utils.js";
import { initKbAutocomplete } from "./kb_autocomplete.js";

let tdDirty = false;
let fbDirty = false;

export function isTdDirty() { return tdDirty; }
export function isFbDirty() { return fbDirty; }

export function refreshTaskDecompForm() {
  const arcId = getArcId();
  return get("/api/arc/" + encodeURIComponent(arcId) + "/task_decomposition").then((data) => {
    const local = loadLocalDraft("td", arcId);
    if (local && local.data && confirm("Restore unsaved Task Decomp draft?")) {
      renderTaskDecompForm(local.data);
      tdDirty = true;
    } else {
      renderTaskDecompForm(data);
      tdDirty = false;
    }
  }).catch(() => {
    const local = loadLocalDraft("td", arcId);
    if (local && local.data && confirm("Restore unsaved Task Decomp draft?")) {
      renderTaskDecompForm(local.data);
      tdDirty = true;
      return;
    }
    renderTaskDecompForm({ arc_id: arcId, encounters: [], opportunities: [], sequence_constraints: [] });
    tdDirty = false;
  });
}

function renderTaskDecompForm(data) {
  const arcId = getArcId();
  document.getElementById("td-arc-id").value = data.arc_id || arcId;
  document.getElementById("td-storyboard-ref").value = data.storyboard_ref || "";
  const encDiv = document.getElementById("td-encounters");
  const encs = data.encounters || [];
  encDiv.innerHTML = encs.map((e, i) => encounterRow(e, i)).join("");
  encDiv.querySelectorAll(".del-enc").forEach((btn) => {
    btn.onclick = () => {
      const d = window._tdData || {};
      d.encounters = (d.encounters || []).filter((_, i) => i !== parseInt(btn.dataset.idx, 10));
      window._tdData = d;
      renderTaskDecompForm(d);
    };
  });
  const oppDiv = document.getElementById("td-opportunities");
  const opps = data.opportunities || [];
  oppDiv.innerHTML = opps.map((o, i) => opportunityRow(o, i)).join("");
  oppDiv.querySelectorAll(".del-opp").forEach((btn) => {
    btn.onclick = () => {
      const d = window._tdData || {};
      d.opportunities = (d.opportunities || []).filter((_, i) => i !== parseInt(btn.dataset.idx, 10));
      window._tdData = d;
      renderTaskDecompForm(d);
    };
  });
  const conDiv = document.getElementById("td-constraints");
  const cons = data.sequence_constraints || [];
  conDiv.innerHTML = cons.map((c, i) => `<div class="form-group"><input type="text" data-constraint-idx="${i}" value="${escapeHtml(c)}" /><button class="del-constraint" data-idx="${i}">Remove</button></div>`).join("");
  conDiv.querySelectorAll(".del-constraint").forEach((btn) => btn.onclick = () => removeConstraint(parseInt(btn.dataset.idx, 10)));
  window._tdData = data;
}

function encounterRow(e, i) {
  return `<div class="form-group" data-enc-idx="${i}">
    <label>Encounter ${i + 1}</label>
    <input type="text" placeholder="id" data-field="id" value="${escapeHtml(e.id || "")}" />
    <input type="text" placeholder="name" data-field="name" value="${escapeHtml(e.name || "")}" />
    <select data-field="type">${ENCOUNTER_TYPES.map((t) => `<option value="${t}"${(e.type || "combat") === t ? " selected" : ""}>${t}</option>`).join("")}</select>
    <input type="number" placeholder="sequence" data-field="sequence" value="${e.sequence != null ? e.sequence : i + 1}" />
    <input type="text" placeholder="storyboard_section" data-field="storyboard_section" value="${escapeHtml(e.storyboard_section || "")}" />
    <input type="text" placeholder="after" data-field="after" value="${escapeHtml(e.after || "")}" />
    <input type="text" placeholder="before" data-field="before" value="${escapeHtml(e.before || "")}" />
    <button class="del-enc" data-idx="${i}">Remove</button>
  </div>`;
}

function opportunityRow(o, i) {
  return `<div class="form-group" data-opp-idx="${i}">
    <label>Opportunity ${i + 1}</label>
    <input type="text" placeholder="id" data-field="id" value="${escapeHtml(o.id || "")}" />
    <input type="text" placeholder="name" data-field="name" value="${escapeHtml(o.name || "")}" />
    <select data-field="type">${ENCOUNTER_TYPES.map((t) => `<option value="${t}"${(o.type || "social") === t ? " selected" : ""}>${t}</option>`).join("")}</select>
    <input type="number" placeholder="sequence" data-field="sequence" value="${o.sequence != null ? o.sequence : i + 1}" />
    <input type="text" placeholder="storyboard_section" data-field="storyboard_section" value="${escapeHtml(o.storyboard_section || "")}" />
    <input type="checkbox" data-field="optional" ${(o.optional !== false) ? "checked" : ""} /> optional
    <input type="text" placeholder="note" data-field="note" value="${escapeHtml(o.note || "")}" />
    <button class="del-opp" data-idx="${i}">Remove</button>
  </div>`;
}

function removeConstraint(idx) {
  const d = window._tdData || {};
  const c = (d.sequence_constraints || []).filter((_, i) => i !== idx);
  d.sequence_constraints = c;
  window._tdData = d;
  renderTaskDecompForm(d);
}

function collectTaskDecomp() {
  const arcIdVal = (document.getElementById("td-arc-id") && document.getElementById("td-arc-id").value || "").trim();
  if (!arcIdVal) return null;
  const d = window._tdData || {};
  const encDiv = document.getElementById("td-encounters");
  const encs = [];
  encDiv.querySelectorAll("[data-enc-idx]").forEach((row) => {
    const idx = parseInt(row.dataset.encIdx, 10);
    encs[idx] = {
      id: row.querySelector("[data-field=id]").value,
      name: row.querySelector("[data-field=name]").value,
      type: row.querySelector("[data-field=type]").value,
      sequence: parseInt(row.querySelector("[data-field=sequence]").value, 10) || idx + 1,
      storyboard_section: row.querySelector("[data-field=storyboard_section]").value,
      after: row.querySelector("[data-field=after]").value || null,
      before: row.querySelector("[data-field=before]").value || null,
    };
  });
  d.encounters = encs.filter(Boolean);
  const oppDiv = document.getElementById("td-opportunities");
  const opps = [];
  oppDiv.querySelectorAll("[data-opp-idx]").forEach((row) => {
    const idx = parseInt(row.dataset.oppIdx, 10);
    const opt = row.querySelector("[data-field=optional]");
    opps[idx] = {
      id: row.querySelector("[data-field=id]").value,
      name: row.querySelector("[data-field=name]").value,
      type: row.querySelector("[data-field=type]").value,
      sequence: parseInt(row.querySelector("[data-field=sequence]").value, 10) || idx + 1,
      optional: opt ? opt.checked : true,
      storyboard_section: row.querySelector("[data-field=storyboard_section]").value,
      note: row.querySelector("[data-field=note]").value,
    };
  });
  d.opportunities = opps.filter(Boolean);
  d.sequence_constraints = [];
  document.querySelectorAll("#td-constraints input[data-constraint-idx]").forEach((inp) => {
    d.sequence_constraints.push(inp.value);
  });
  d.arc_id = document.getElementById("td-arc-id").value || getArcId();
  d.storyboard_ref = document.getElementById("td-storyboard-ref").value;
  return d;
}

export function initTaskDecompHandlers() {
  const panelForm1 = document.getElementById("panel-form1");
  if (panelForm1) panelForm1.addEventListener("input", () => {
    tdDirty = true;
    const draft = collectTaskDecomp();
    if (draft) saveLocalDraft("td", getArcId(), draft);
  });
  if (panelForm1) panelForm1.addEventListener("change", () => {
    tdDirty = true;
    const draft = collectTaskDecomp();
    if (draft) saveLocalDraft("td", getArcId(), draft);
  });

  document.getElementById("td-add-enc").addEventListener("click", () => {
    const d = window._tdData || { arc_id: getArcId(), encounters: [], opportunities: [], sequence_constraints: [] };
    d.encounters = d.encounters || [];
    d.encounters.push({ id: "enc_" + d.encounters.length, name: "", type: "combat", sequence: d.encounters.length + 1, storyboard_section: "", after: null, before: null });
    window._tdData = d;
    renderTaskDecompForm(d);
  });
  document.getElementById("td-add-opp").addEventListener("click", () => {
    const d = window._tdData || { arc_id: getArcId(), encounters: [], opportunities: [], sequence_constraints: [] };
    d.opportunities = d.opportunities || [];
    d.opportunities.push({ id: "opp_" + d.opportunities.length, name: "", type: "social", sequence: 1, optional: true, storyboard_section: "", note: "" });
    window._tdData = d;
    renderTaskDecompForm(d);
  });
  document.getElementById("td-add-constraint").addEventListener("click", () => {
    const d = window._tdData || { arc_id: getArcId(), encounters: [], opportunities: [], sequence_constraints: [] };
    d.sequence_constraints = d.sequence_constraints || [];
    d.sequence_constraints.push("");
    window._tdData = d;
    renderTaskDecompForm(d);
  });

  document.getElementById("save-td").addEventListener("click", () => {
    const d = collectTaskDecomp();
    if (!d) { setValidationErrors("td-errors", ["arc_id is required."]); return; }
    const errs = validateTaskDecomp(d);
    setValidationErrors("td-errors", errs);
    if (errs.length) return;
    put("/api/arc/" + encodeURIComponent(getArcId()) + "/task_decomposition", d)
      .then((r) => {
        tdDirty = false;
        clearLocalDraft("td", getArcId());
        alert("Saved: " + (r.path || r.status));
      })
      .catch((e) => showFileModal("Error", formatErr(e), "", true));
  });
}

export function refreshFeedbackForm() {
  const arcId = getArcId();
  return get("/api/arc/" + encodeURIComponent(arcId) + "/feedback").then((data) => {
    const local = loadLocalDraft("fb", arcId);
    if (local && local.data && confirm("Restore unsaved Feedback draft?")) {
      renderFeedbackForm(local.data);
      fbDirty = true;
    } else {
      renderFeedbackForm(data);
      fbDirty = false;
    }
  }).catch(() => {
    const local = loadLocalDraft("fb", arcId);
    if (local && local.data && confirm("Restore unsaved Feedback draft?")) {
      renderFeedbackForm(local.data);
      fbDirty = true;
      return;
    }
    renderFeedbackForm({ arc_id: arcId, encounters: [] });
    fbDirty = false;
  });
}

function renderFeedbackForm(data) {
  const arcId = getArcId();
  const encIds = (data.encounters || []).map((e) => e.id);
  const sel = document.getElementById("fb-encounter");
  sel.innerHTML = "<option value=\"\">(select encounter)</option>" + encIds.map((id) => `<option value="${escapeHtml(id)}">${escapeHtml(id)}</option>`).join("");
  if (encIds.length === 0) {
    get("/api/arc/" + encodeURIComponent(arcId) + "/task_decomposition").then((td) => {
      const ids = (td.encounters || []).map((e) => e.id);
      sel.innerHTML = "<option value=\"\">(select encounter)</option>" + ids.map((id) => `<option value="${escapeHtml(id)}">${escapeHtml(id)}</option>`).join("");
    }).catch(() => {});
  }
  const itemsDiv = document.getElementById("fb-items");
  const enc = (data.encounters || [])[0];
  const items = enc ? (enc.feedback || []) : [];
  itemsDiv.innerHTML = items.map((it, i) => feedbackItemRow(it, i)).join("");
  itemsDiv.querySelectorAll(".del-fb").forEach((btn) => btn.onclick = () => removeFeedbackItem(parseInt(btn.dataset.idx, 10)));
  initKbAutocomplete(itemsDiv);
  window._fbData = data;
}

function feedbackItemRow(it, i) {
  const t = it.type || "other";
  const typeOpts = FEEDBACK_TYPES.map((x) => `<option value="${x}"${x === t ? " selected" : ""}>${x}</option>`).join("");
  const fields = typeFields(t, it);
  return `<div class="form-group feedback-item" data-fb-idx="${i}">
    <select class="fb-type">${typeOpts}</select>
    ${fields}
    <button class="del-fb" data-idx="${i}">Remove</button>
  </div>`;
}

function typeFields(t, it) {
  const F = {
    expand: () => `<input placeholder="target" value="${escapeHtml(it.target || "")}" data-f="target" /><input placeholder="instruction" value="${escapeHtml(it.instruction || "")}" data-f="instruction" />`,
    change: () => `<input placeholder="target" value="${escapeHtml(it.target || "")}" data-f="target" /><input placeholder="from" value="${escapeHtml(it.from != null ? it.from : "")}" data-f="from" /><input placeholder="to" value="${escapeHtml(it.to != null ? it.to : "")}" data-f="to" />`,
    add_mechanic: () => `<input placeholder="detail" value="${escapeHtml(it.detail || "")}" data-f="detail" />`,
    remove: () => `<input placeholder="target or instruction" value="${escapeHtml(it.target || it.instruction || "")}" data-f="target" />`,
    link_npc: () => `<input placeholder="npc_id" value="${escapeHtml(it.npc_id || "")}" data-f="npc_id" data-autocomplete="npc" /><input placeholder="instruction" value="${escapeHtml(it.instruction || "")}" data-f="instruction" />`,
    link_location: () => `<input placeholder="location_id" value="${escapeHtml(it.location_id || "")}" data-f="location_id" data-autocomplete="location" /><input placeholder="instruction" value="${escapeHtml(it.instruction || "")}" data-f="instruction" />`,
    other: () => `<input placeholder="instruction or detail" value="${escapeHtml(it.instruction || it.detail || "")}" data-f="instruction" />`,
  };
  return (F[t] || F.other)();
}

function removeFeedbackItem(idx) {
  const d = window._fbData || {};
  const encId = document.getElementById("fb-encounter").value;
  const enc = (d.encounters || []).find((e) => e.id === encId);
  if (enc && enc.feedback) enc.feedback = enc.feedback.filter((_, i) => i !== idx);
  window._fbData = d;
  renderFeedbackForm(d);
}

function collectFeedback() {
  const d = window._fbData || { arc_id: getArcId(), encounters: [] };
  const encId = document.getElementById("fb-encounter").value;
  if (!encId) return null;
  let enc = (d.encounters || []).find((e) => e.id === encId);
  if (!enc) enc = { id: encId, feedback: [] };
  d.encounters = d.encounters || [];
  const idx = d.encounters.findIndex((e) => e.id === encId);
  if (idx >= 0) d.encounters[idx] = enc; else d.encounters.push(enc);
  const itemsDiv = document.getElementById("fb-items");
  enc.feedback = [];
  itemsDiv.querySelectorAll(".feedback-item").forEach((row) => {
    const type = row.querySelector(".fb-type").value;
    const obj = { type };
    row.querySelectorAll("[data-f]").forEach((inp) => { obj[inp.getAttribute("data-f")] = inp.value; });
    enc.feedback.push(obj);
  });
  d.arc_id = getArcId();
  return d;
}

export function initFeedbackHandlers() {
  const panelForm3 = document.getElementById("panel-form3");
  if (panelForm3) panelForm3.addEventListener("input", () => {
    fbDirty = true;
    const draft = collectFeedback();
    if (draft) saveLocalDraft("fb", getArcId(), draft);
  });
  if (panelForm3) panelForm3.addEventListener("change", () => {
    fbDirty = true;
    const draft = collectFeedback();
    if (draft) saveLocalDraft("fb", getArcId(), draft);
  });

  document.getElementById("fb-add").addEventListener("click", () => {
    const d = window._fbData || { arc_id: getArcId(), encounters: [] };
    const encId = document.getElementById("fb-encounter").value;
    if (!encId) { alert("Select an encounter first."); return; }
    let enc = (d.encounters || []).find((e) => e.id === encId);
    if (!enc) { enc = { id: encId, feedback: [] }; d.encounters = d.encounters || []; d.encounters.push(enc); }
    enc.feedback = enc.feedback || [];
    enc.feedback.push({ type: "other", instruction: "" });
    window._fbData = d;
    renderFeedbackForm(d);
  });

  document.getElementById("save-fb").addEventListener("click", () => {
    const d = collectFeedback();
    if (!d) { setValidationErrors("fb-errors", ["Select an encounter first."]); return; }
    const errs = validateFeedback(d);
    setValidationErrors("fb-errors", errs);
    if (errs.length) return;
    put("/api/arc/" + encodeURIComponent(getArcId()) + "/feedback", d)
      .then((r) => {
        fbDirty = false;
        clearLocalDraft("fb", getArcId());
        alert("Saved: " + (r.path || r.status));
      })
      .catch((e) => showFileModal("Error", formatErr(e), "", true));
  });

  document.getElementById("fb-encounter").addEventListener("change", () => {
    const encId = document.getElementById("fb-encounter").value;
    const d = window._fbData || {};
    const enc = (d.encounters || []).find((e) => e.id === encId);
    const items = enc ? (enc.feedback || []) : [];
    const itemsDiv = document.getElementById("fb-items");
    itemsDiv.innerHTML = items.map((it, i) => feedbackItemRow(it, i)).join("");
    itemsDiv.querySelectorAll(".del-fb").forEach((btn) => {
      btn.onclick = () => removeFeedbackItem(parseInt(btn.dataset.idx, 10));
    });
    initKbAutocomplete(itemsDiv);
  });
}

export function refreshS4Drafts() {
  const arcId = getArcId();
  return get("/api/arc/" + encodeURIComponent(arcId) + "/tree").then((d) => {
    const paths = (d.encounters || []).concat(d.opportunities || []).map((e) => e.path);
    const sel = document.getElementById("s4-draft");
    sel.innerHTML = "<option value=\"\">(select draft)</option>" + paths.map((p) => `<option value="${escapeHtml(p)}">${escapeHtml(p.split(/[/\\]/).pop())}</option>`).join("");
  }).catch(() => {});
}
