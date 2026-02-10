// PURPOSE: Campaign KB panel behaviors.
// DEPENDENCIES: api.js, utils.js
// MODIFICATION NOTES: Extracted from app.js.

import { get, post } from "./api.js";
import { formatErr } from "./utils.js";

function setKbStatus(text, isErr) {
  const el = document.getElementById("kb-status");
  if (el) { el.textContent = text; el.className = isErr ? "err" : "ok"; }
}

export function refreshKbStatus() {
  setKbStatus("Checking…");
  get("/api/kb/status").then((d) => {
    setKbStatus(d.status === "ok" ? "OK (" + (d.campaign_kb_url || "") + ")" : (d.error || "Unknown"), !!d.error);
  }).catch((e) => {
    setKbStatus("Error: " + formatErr(e), true);
  });
}

function setKbSearchResults(content, isErr) {
  const el = document.getElementById("kb-search-results");
  if (!el) return;
  el.innerHTML = "";
  const pre = document.createElement("pre");
  pre.className = isErr ? "err" : "ok";
  pre.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
  el.appendChild(pre);
}

function setKbMergeOut(content, isErr) {
  const el = document.getElementById("kb-merge-out");
  if (!el) return;
  el.innerHTML = "";
  const pre = document.createElement("pre");
  pre.className = isErr ? "err" : "ok";
  pre.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
  el.appendChild(pre);
}

export function initKbHandlers() {
  const kbCheckBtn = document.getElementById("kb-check-status");
  if (kbCheckBtn) kbCheckBtn.addEventListener("click", refreshKbStatus);
  const kbSearchBtn = document.getElementById("kb-search-btn");
  if (kbSearchBtn) kbSearchBtn.addEventListener("click", function () {
    const q = document.getElementById("kb-search-query");
    const query = (q && q.value || "").trim();
    if (!query) { setKbSearchResults("Enter a search query.", true); return; }
    kbSearchBtn.disabled = true;
    setKbSearchResults("Searching…");
    get("/api/kb/search?query=" + encodeURIComponent(query) + "&limit=20").then((d) => {
      setKbSearchResults(d);
      if (d.results && d.results.length === 0) setKbSearchResults(d.query ? "No results for: " + d.query : d);
    }).catch((e) => setKbSearchResults(formatErr(e), true)).finally(() => { kbSearchBtn.disabled = false; });
  });
  const kbIngestBtn = document.getElementById("kb-ingest-pdfs");
  if (kbIngestBtn) kbIngestBtn.addEventListener("click", function () {
    const pdfRoot = (document.getElementById("kb-pdf-root") && document.getElementById("kb-pdf-root").value || "").trim();
    kbIngestBtn.disabled = true;
    setKbSearchResults("Ingesting PDFs…");
    post("/api/kb/ingest/pdfs", pdfRoot ? { pdf_root: pdfRoot } : {}).then((d) => {
      setKbSearchResults(d);
    }).catch((e) => setKbSearchResults(formatErr(e), true)).finally(() => { kbIngestBtn.disabled = false; });
  });
  const kbMergeBtn = document.getElementById("kb-merge");
  if (kbMergeBtn) kbMergeBtn.addEventListener("click", function () {
    kbMergeBtn.disabled = true;
    setKbMergeOut("Running merge…");
    post("/api/kb/merge", {}).then((d) => {
      setKbMergeOut(d);
      if (d.output_path) setKbMergeOut("Output: " + d.output_path + "\nCitations: " + (d.citations_included || 0) + "\n\n" + JSON.stringify(d, null, 2));
    }).catch((e) => setKbMergeOut(formatErr(e), true)).finally(() => { kbMergeBtn.disabled = false; });
  });
}
