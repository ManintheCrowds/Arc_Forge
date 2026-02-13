// PURPOSE: KB autocomplete for npc_id and location_id feedback fields.
// DEPENDENCIES: api.js
// MODIFICATION NOTES: UW-7 cross-links to campaign_kb.

import { get } from "./api.js";

const DEBOUNCE_MS = 250;
const LIMIT = 10;

/**
 * Attach KB autocomplete to an input. On input/focus, debounced search; show dropdown below input; on select fill value.
 * @param {HTMLInputElement} inputEl - Target input
 * @param {string} resultKey - Key to use for value: "document_title", "section_id", or "path"
 * @param {{ source_name?: string, doc_type?: string }} opts - Optional filters for NPC vs location
 */
export function kbAutocomplete(inputEl, resultKey = "document_title", opts = {}) {
  if (!inputEl) return;
  let debounceTimer = null;
  let dropdown = null;

  function hideDropdown() {
    if (dropdown && dropdown.parentNode) dropdown.parentNode.removeChild(dropdown);
    dropdown = null;
  }

  function showDropdown(items) {
    hideDropdown();
    if (!items || items.length === 0) return;
    dropdown = document.createElement("div");
    dropdown.className = "kb-autocomplete-dropdown";
    dropdown.style.cssText = "position:absolute; background:var(--panel, #1a1a1a); border:1px solid var(--border); border-radius:6px; max-height:200px; overflow-y:auto; z-index:1000; box-shadow:0 4px 12px rgba(0,0,0,0.3);";
    items.forEach((item) => {
      const val = item[resultKey] ?? item.document_title ?? String(item.section_id ?? "");
      const disp = item.document_title || val;
      const div = document.createElement("div");
      div.className = "kb-autocomplete-item";
      div.style.cssText = "padding:0.4rem 0.75rem; cursor:pointer; font-size:12px;";
      div.textContent = disp;
      div.addEventListener("mouseenter", () => div.style.background = "var(--hover, #333)");
      div.addEventListener("mouseleave", () => div.style.background = "");
      div.addEventListener("click", () => {
        inputEl.value = val;
        inputEl.dispatchEvent(new Event("input", { bubbles: true }));
        hideDropdown();
      });
      dropdown.appendChild(div);
    });
    const rect = inputEl.getBoundingClientRect();
    dropdown.style.position = "fixed";
    dropdown.style.top = `${rect.bottom}px`;
    dropdown.style.left = `${rect.left}px`;
    dropdown.style.minWidth = `${rect.width}px`;
    document.body.appendChild(dropdown);
    document.addEventListener("click", closeOnClickOutside);
  }

  function closeOnClickOutside(e) {
    if (dropdown && !dropdown.contains(e.target) && e.target !== inputEl) {
      hideDropdown();
      document.removeEventListener("click", closeOnClickOutside);
    }
  }

  function doSearch() {
    const q = (inputEl.value || "").trim();
    if (!q || q.length < 1) {
      hideDropdown();
      return;
    }
    const params = new URLSearchParams({ query: q, limit: String(LIMIT) });
    if (opts.source_name) params.set("source_name", opts.source_name);
    if (opts.doc_type) params.set("doc_type", opts.doc_type);
    get("/api/kb/search?" + params.toString())
      .then((d) => {
        const items = (d && d.results) || [];
        showDropdown(items);
      })
      .catch(() => hideDropdown());
  }

  function debouncedSearch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(doSearch, DEBOUNCE_MS);
  }

  inputEl.addEventListener("input", debouncedSearch);
  inputEl.addEventListener("focus", () => {
    if ((inputEl.value || "").trim().length >= 1) debouncedSearch();
  });
  inputEl.addEventListener("blur", () => {
    setTimeout(hideDropdown, 150);
  });
}

/**
 * Initialize autocomplete for all [data-autocomplete] inputs within container.
 * data-autocomplete="npc" | "location" maps to optional doc_type/source_name.
 */
export function initKbAutocomplete(container) {
  if (!container) return;
  container.querySelectorAll("[data-autocomplete]").forEach((inp) => {
    const kind = inp.getAttribute("data-autocomplete");
    const opts = kind === "npc" ? { doc_type: "npc" } : kind === "location" ? { doc_type: "location" } : {};
    kbAutocomplete(inp, "document_title", opts);
  });
}
