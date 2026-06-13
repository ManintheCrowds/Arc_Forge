// PURPOSE: Note editor for Workbench (load, save, preview, save-card).
// DEPENDENCIES: api.js, utils.js
// MODIFICATION NOTES: Phase 3 note editor.

import { escapeHtml, formatErr } from "./utils.js";

let _activeCampaign = "";
let _activePath = "";
let _activeSubpath = "";
let _previewVisible = false;
let _loadSeq = 0;
let _loaded = false;
let _lastLoadedContent = "";
let _dirty = false;

function getCampaign() {
  const sel = document.getElementById("module-campaign");
  return (sel && sel.value) || "first_arc";
}

function toSubpath(path, campaign) {
  if (!path) return "";
  const prefix = campaign + "/";
  return path.startsWith(prefix) ? path.slice(prefix.length) : path;
}

function showFeedback(msg, isErr = false) {
  const out = document.getElementById("note-editor-out");
  if (!out) return;
  out.textContent = msg;
  out.className = "out " + (isErr ? "err" : "ok");
  out.style.display = "block";
  setTimeout(() => { out.style.display = "none"; }, 3000);
}

function resetPreview(preview) {
  _previewVisible = false;
  if (preview) {
    preview.style.display = "none";
    preview.innerHTML = "";
  }
}

function markClean(content) {
  _lastLoadedContent = content || "";
  _dirty = false;
  _loaded = true;
}

function clearActiveNote(editor, preview) {
  _loadSeq += 1;
  _activeCampaign = "";
  _activePath = "";
  _activeSubpath = "";
  _loaded = false;
  _lastLoadedContent = "";
  _dirty = false;
  document.body.setAttribute("data-active-note-path", "");
  if (editor) {
    editor.value = "";
    editor.placeholder = "Select a note to edit...";
  }
  resetPreview(preview);
}

function isCurrentLoad(loadSeq, campaign, subpath) {
  return loadSeq === _loadSeq && campaign === _activeCampaign && subpath === _activeSubpath;
}

function confirmDiscardUnsaved() {
  if (!_dirty) return true;
  if (typeof window.confirm !== "function") return false;
  return window.confirm("Discard unsaved note changes?");
}

function renderMarkdown(text) {
  if (typeof marked !== "undefined" && marked.parse) {
    return marked.parse(text || "");
  }
  return escapeHtml(text || "").replace(/\n/g, "<br>");
}

export function initNoteEditor() {
  const editor = document.getElementById("note-editor");
  const preview = document.getElementById("note-preview");
  const saveBtn = document.getElementById("save-note");
  const saveCardBtn = document.getElementById("save-card");
  const toggleBtn = document.getElementById("toggle-preview");

  window.addEventListener("workbench:tree-select", (e) => {
    const path = e.detail && e.detail.path;
    if (!path || !editor) return;
    if (!confirmDiscardUnsaved()) return;
    const campaign = getCampaign();
    const subpath = toSubpath(path, campaign);
    const loadSeq = _loadSeq + 1;
    _loadSeq = loadSeq;
    _activeCampaign = campaign;
    _activePath = path;
    _activeSubpath = subpath;
    _loaded = false;
    _lastLoadedContent = "";
    _dirty = false;
    document.body.setAttribute("data-active-note-path", path || "");
    editor.value = "";
    editor.placeholder = "Loading…";
    fetch("/api/arc/" + encodeURIComponent(campaign) + "/file/" + encodeURIComponent(subpath))
      .then((r) => (r.ok ? r.text() : Promise.reject(new Error(r.status + " " + r.statusText))))
      .then((text) => {
        if (!isCurrentLoad(loadSeq, campaign, subpath)) return;
        editor.value = text || "";
        editor.placeholder = "Select a note to edit...";
        markClean(editor.value);
      })
      .catch((err) => {
        if (!isCurrentLoad(loadSeq, campaign, subpath)) return;
        editor.placeholder = "Select a note to edit...";
        editor.value = "";
        _activePath = "";
        _activeSubpath = "";
        _loaded = false;
        _lastLoadedContent = "";
        _dirty = false;
        document.body.setAttribute("data-active-note-path", "");
        showFeedback("Load failed: " + formatErr(err), true);
      });
    resetPreview(preview);
  });

  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      if (!_loaded || !_activeCampaign || !_activeSubpath || !editor) return;
      const campaign = _activeCampaign;
      const content = editor.value || "";
      fetch("/api/arc/" + encodeURIComponent(campaign) + "/file/" + encodeURIComponent(_activeSubpath), {
        method: "PUT",
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: content,
      }).then((r) => {
        if (r.ok) return r.json();
        return r.json().then((e) => Promise.reject(e)).catch(() => Promise.reject(new Error(r.status + " " + r.statusText)));
      })
        .then(() => {
          markClean(content);
          showFeedback("Saved.");
        })
        .catch((err) => showFeedback("Save failed: " + formatErr(err), true));
    });
  }

  if (toggleBtn && preview) {
    toggleBtn.addEventListener("click", () => {
      _previewVisible = !_previewVisible;
      preview.style.display = _previewVisible ? "block" : "none";
      if (_previewVisible) {
        preview.innerHTML = renderMarkdown(editor ? editor.value : "");
      }
    });
  }

  if (editor && preview) {
    editor.addEventListener("input", () => {
      _dirty = _loaded ? editor.value !== _lastLoadedContent : Boolean(editor.value);
      if (_previewVisible) {
        preview.innerHTML = renderMarkdown(editor.value);
      }
    });
  }

  if (saveCardBtn) {
    saveCardBtn.addEventListener("click", () => {
      if (!_loaded || !_activeCampaign || !_activeSubpath || !editor) return;
      const campaign = _activeCampaign;
      let content = editor.value || "";
      if (!content.includes("---")) {
        content = "---\ntype: note\ntitle: " + (_activePath.split("/").pop() || "Note").replace(".md", "") + "\n---\n\n" + content;
      }
      fetch("/api/arc/" + encodeURIComponent(campaign) + "/file/" + encodeURIComponent(_activeSubpath), {
        method: "PUT",
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: content,
      }).then((r) => {
        if (r.ok) return r.json();
        return r.json().then((e) => Promise.reject(e)).catch(() => Promise.reject(new Error(r.status + " " + r.statusText)));
      })
        .then(() => {
          editor.value = content;
          markClean(content);
          if (_previewVisible && preview) {
            preview.innerHTML = renderMarkdown(content);
          }
          showFeedback("Saved as card.");
        })
        .catch((err) => showFeedback("Save failed: " + formatErr(err), true));
    });
  }

  // Sync campaign when module-campaign changes
  const campaignSel = document.getElementById("module-campaign");
  if (campaignSel) {
    campaignSel.addEventListener("change", () => {
      if (!confirmDiscardUnsaved()) {
        campaignSel.value = _activeCampaign || campaignSel.value || "first_arc";
        return;
      }
      clearActiveNote(editor, preview);
    });
  }
}
