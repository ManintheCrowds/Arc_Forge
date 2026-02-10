// PURPOSE: Workflow GUI frontend. Pipeline view, arc tree, stage run, Stage 1/3 forms, provenance.
(function () {
  const API = "";
  let arcId = "first_arc";
  let artifacts = {};
  let tdDirty = false;
  let fbDirty = false;
  let moduleCampaign = "";
  let moduleName = "";
  let activeNotePath = "";
  let showPreview = true;
  const FEEDBACK_TYPES = ["expand", "change", "add_mechanic", "remove", "link_npc", "link_location", "other"];
  const ENCOUNTER_TYPES = ["combat", "social", "exploration", "environmental"];

  function formatErr(e) {
    if (!e) return "Unknown error";
    if (typeof e === "string") return e;
    return e.error || e.reason || e.detail || e.message || JSON.stringify(e);
  }

  function setProgress(id, active) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.toggle("active", !!active);
  }

  function setValidationErrors(id, errors) {
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

  function loadLocalDraft(kind) {
    try {
      const raw = localStorage.getItem("workflow_ui:" + kind + ":draft:" + arcId);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function saveLocalDraft(kind, data) {
    try {
      localStorage.setItem(
        "workflow_ui:" + kind + ":draft:" + arcId,
        JSON.stringify({ savedAt: Date.now(), data: data })
      );
    } catch (e) {}
  }

  function clearLocalDraft(kind) {
    try {
      localStorage.removeItem("workflow_ui:" + kind + ":draft:" + arcId);
    } catch (e) {}
  }

  function validateTaskDecomp(data) {
    const errors = [];
    if (!data.arc_id) errors.push("arc_id is required.");
    const encs = data.encounters || [];
    encs.forEach((e, i) => {
      if (!e.id) errors.push("encounters[" + i + "].id is required.");
      if (!e.name) errors.push("encounters[" + i + "].name is required.");
      if (!e.type) errors.push("encounters[" + i + "].type is required.");
      if (e.type && ENCOUNTER_TYPES.indexOf(e.type) === -1) {
        errors.push("encounters[" + i + "].type must be one of: " + ENCOUNTER_TYPES.join(", "));
      }
      if (e.sequence == null || Number.isNaN(Number(e.sequence))) {
        errors.push("encounters[" + i + "].sequence must be a number.");
      }
    });
    const opps = data.opportunities || [];
    opps.forEach((o, i) => {
      if (!o.id) errors.push("opportunities[" + i + "].id is required.");
      if (!o.name) errors.push("opportunities[" + i + "].name is required.");
      if (!o.type) errors.push("opportunities[" + i + "].type is required.");
      if (o.type && ENCOUNTER_TYPES.indexOf(o.type) === -1) {
        errors.push("opportunities[" + i + "].type must be one of: " + ENCOUNTER_TYPES.join(", "));
      }
      if (o.sequence == null || Number.isNaN(Number(o.sequence))) {
        errors.push("opportunities[" + i + "].sequence must be a number.");
      }
    });
    return errors;
  }

  function validateFeedback(data) {
    const errors = [];
    if (!data.arc_id) errors.push("arc_id is required.");
    const encs = data.encounters || [];
    encs.forEach((enc, i) => {
      if (!enc.id) errors.push("encounters[" + i + "].id is required.");
      const items = enc.feedback || [];
      items.forEach((it, j) => {
        const base = "encounters[" + i + "].feedback[" + j + "]";
        if (!it.type) errors.push(base + ".type is required.");
        if (it.type && FEEDBACK_TYPES.indexOf(it.type) === -1) {
          errors.push(base + ".type must be one of: " + FEEDBACK_TYPES.join(", "));
        }
        const has = (k) => it[k] != null && String(it[k]).trim() !== "";
        if (it.type === "expand" && !(has("target") && has("instruction"))) {
          errors.push(base + " requires target and instruction.");
        } else if (it.type === "change" && !(has("target") && (has("to") || has("instruction")))) {
          errors.push(base + " requires target and to (or instruction).");
        } else if (it.type === "add_mechanic" && !has("detail")) {
          errors.push(base + " requires detail.");
        } else if (it.type === "remove" && !(has("target") || has("instruction"))) {
          errors.push(base + " requires target or instruction.");
        } else if (it.type === "link_npc" && !(has("npc_id") && has("instruction"))) {
          errors.push(base + " requires npc_id and instruction.");
        } else if (it.type === "link_location" && !(has("location_id") && has("instruction"))) {
          errors.push(base + " requires location_id and instruction.");
        } else if (it.type === "other" && !(has("instruction") || has("detail"))) {
          errors.push(base + " requires instruction or detail.");
        }
      });
    });
    return errors;
  }

  function get(url) {
    return fetch(API + url).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
  }
  function post(url, body) {
    return fetch(API + url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
  }
  function put(url, body) {
    return fetch(API + url, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
  }

  function showWorkspace(name) {
    document.querySelectorAll(".workspace-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.workspace === name));
    document.querySelectorAll(".workspace-view").forEach((v) => v.classList.toggle("visible", v.id === "workspace-" + name));
  }

  function showRightPanel(name) {
    document.querySelectorAll(".right-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.right === name));
    document.querySelectorAll(".right-panel").forEach((p) => p.classList.toggle("visible", p.id === "right-" + name));
  }

  function showBottomPanel(name) {
    document.querySelectorAll(".bottom-tabs button").forEach((b) => b.classList.toggle("active", b.dataset.bottom === name));
    document.querySelectorAll(".bottom-panel").forEach((p) => p.classList.toggle("visible", p.id === "bottom-" + name));
  }

  function setCreateModuleOut(content, isErr) {
    const el = document.getElementById("create-module-out");
    if (!el) return;
    el.innerHTML = "";
    const pre = document.createElement("pre");
    pre.className = isErr ? "err" : "ok";
    pre.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
    el.appendChild(pre);
  }

  function setEditorContent(path, text) {
    activeNotePath = path || "";
    const editor = document.getElementById("note-editor");
    if (editor) editor.value = text || "";
    renderPreview();
    renderNoteTabs();
  }

  function renderPreview() {
    const preview = document.getElementById("note-preview");
    const editor = document.getElementById("note-editor");
    if (!preview || !editor) return;
    preview.style.display = showPreview ? "block" : "none";
    if (!showPreview) return;
    preview.textContent = editor.value || "";
  }

  function renderNoteTabs() {
    const tabs = document.getElementById("note-tabs");
    if (!tabs) return;
    if (!activeNotePath) {
      tabs.innerHTML = "<span class=\"muted\">No note open</span>";
      return;
    }
    const label = activeNotePath.split("/").pop() || activeNotePath;
    tabs.innerHTML = `<button class="active">${escapeHtml(label)}</button>`;
  }

  function refreshModules() {
    get("/api/modules").then((d) => {
      const campaignSel = document.getElementById("module-campaign");
      const moduleSel = document.getElementById("module-select");
      const campaigns = d.campaigns || [];
      if (!campaignSel || !moduleSel) return;
      if (!campaigns.length) {
        campaignSel.innerHTML = "<option value=\"\">(no campaigns)</option>";
        moduleSel.innerHTML = "<option value=\"\">(no modules)</option>";
        return;
      }
      campaignSel.innerHTML = campaigns.map((c) => `<option value="${escapeHtml(c.name)}">${escapeHtml(c.name)}</option>`).join("");
      moduleCampaign = moduleCampaign || (campaigns[0] && campaigns[0].name) || "";
      campaignSel.value = moduleCampaign;
      const mods = (campaigns.find((c) => c.name === moduleCampaign) || {}).modules || [];
      moduleSel.innerHTML = mods.map((m) => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
      moduleName = moduleName || mods[0] || "";
      moduleSel.value = moduleName;
      refreshModuleTree();
      campaignSel.onchange = () => {
        moduleCampaign = campaignSel.value;
        moduleName = "";
        refreshModules();
      };
      moduleSel.onchange = () => {
        moduleName = moduleSel.value;
        refreshModuleTree();
      };
    }).catch(() => {});
  }

  function refreshModuleTree() {
    if (!moduleCampaign || !moduleName) return;
    get("/api/modules/" + encodeURIComponent(moduleCampaign) + "/" + encodeURIComponent(moduleName) + "/tree")
      .then((d) => {
        const treeEl = document.getElementById("module-tree");
        if (!treeEl) return;
        const typeFilter = (document.getElementById("filter-type") && document.getElementById("filter-type").value) || "";
        const files = (d.files || []).filter((f) => {
          if (!typeFilter) return true;
          const path = (f.rel || f.path || "").toLowerCase();
          if (typeFilter === "scene") return path.indexOf("/scenes/") !== -1;
          if (typeFilter === "npc") return path.indexOf("/npcs/") !== -1;
          if (typeFilter === "location") return path.indexOf("/locations/") !== -1;
          if (typeFilter === "faction") return path.indexOf("/factions/") !== -1;
          return true;
        });
        treeEl.innerHTML = files.map((f) => `<div class="file"><a href="#" data-path="${escapeHtml(f.rel)}">${escapeHtml(f.rel)}</a></div>`).join("") || "<div class=\"muted\">(no files)</div>";
        treeEl.querySelectorAll("a[data-path]").forEach((a) => {
          a.onclick = (ev) => {
            ev.preventDefault();
            viewModuleFile(a.getAttribute("data-path"));
          };
        });
      }).catch(() => {});
  }

  function viewModuleFile(relPath) {
    if (!moduleCampaign || !moduleName || !relPath) return;
    const url = "/api/modules/" + encodeURIComponent(moduleCampaign) + "/" + encodeURIComponent(moduleName) + "/file/" + encodeURIComponent(relPath.replace(/\\/g, "/"));
    fetch(url).then((r) => {
      if (!r.ok) {
        return r.json().then((j) => {
          showFileModal("Not found", formatErr(j) || relPath, "", true);
        }).catch(() => showFileModal("Not found", relPath, "", true));
        return;
      }
      return r.text().then((text) => {
        setEditorContent(relPath, text);
      });
    }).catch((e) => showFileModal("Error", formatErr(e), "", true));
  }

  function setArc(id) {
    arcId = id || "first_arc";
    refreshTree();
    refreshArtifacts();
    refreshTaskDecompForm();
    refreshFeedbackForm();
    refreshS4Drafts();
  }

  function refreshArcs() {
    get("/api/arcs").then((d) => {
      const sel = document.getElementById("arc-select");
      sel.innerHTML = d.arcs.length ? d.arcs.map((a) => `<option${a === arcId ? " selected" : ""}>${a}</option>`).join("") : "<option>first_arc</option>";
      sel.value = arcId;
      sel.onchange = () => setArc(sel.value);
    }).catch(() => {});
  }

  function refreshTree() {
    get("/api/arc/" + encodeURIComponent(arcId) + "/tree").then((d) => {
      const treeEl = document.getElementById("arc-tree");
      const files = (d.files || []).map((f) => `<li class="file">${f.name}</li>`).join("");
      treeEl.innerHTML = files || "<li class=\"file\">(no files)</li>";

      const encList = document.getElementById("encounters-list");
      const enc = (d.encounters || []).concat(d.opportunities || []).map((e) => {
        const prov = [];
        if (e.version) prov.push(e.version);
        if (e.source) prov.push("from " + e.source);
        const rel = e.rel || e.path;
        return `<div><a href="#" data-rel="${escapeHtml(rel)}">${escapeHtml(e.name)}</a><div class="provenance">${prov.map((p) => `<span>${escapeHtml(p)}</span>`).join("")}</div></div>`;
      }).join("");
      encList.innerHTML = enc || "<div class=\"muted\">(no encounters yet)</div>";
      encList.querySelectorAll("a[data-rel]").forEach((a) => {
        a.onclick = (ev) => {
          ev.preventDefault();
          viewFile(a.getAttribute("data-rel"));
        };
      });
    }).catch(() => {});
  }

  function escapeHtml(s) {
    if (s == null) return "";
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function showFileModal(title, content, note, isErr) {
    const modal = document.getElementById("file-modal");
    const modalTitle = document.getElementById("file-modal-title");
    const modalContent = document.getElementById("file-modal-content");
    const modalNote = document.getElementById("file-modal-note");
    if (!modal || !modalTitle || !modalContent || !modalNote) {
      alert(title + ":\n\n" + content);
      return;
    }
    modalTitle.textContent = title;
    modalContent.textContent = content || "";
    modalNote.textContent = note || "";
    modal.classList.toggle("is-error", !!isErr);
    modal.classList.add("visible");
  }

  function closeFileModal() {
    const modal = document.getElementById("file-modal");
    if (modal) {
      modal.classList.remove("visible");
      modal.classList.remove("is-error");
    }
  }

  function viewFile(relPath) {
    const url = "/api/arc/" + encodeURIComponent(arcId) + "/file/" + encodeURIComponent(relPath.replace(/\\/g, "/"));
    fetch(url).then((r) => {
      if (!r.ok) {
        return r.json().then((j) => {
          showFileModal("Not found", formatErr(j) || relPath, "", true);
        }).catch(() => showFileModal("Not found", relPath, "", true));
        return;
      }
      return r.text().then((text) => {
        const maxLen = 50000;
        const truncated = text.length > maxLen;
        const display = truncated ? text.slice(0, maxLen) + "\n… (truncated)" : text;
        const note = truncated ? "Note: file content truncated for display." : "";
        showFileModal(relPath, display, note, false);
      });
    }).catch((e) => showFileModal("Error", formatErr(e), "", true));
  }

  function refreshArtifacts() {
    get("/api/arc/" + encodeURIComponent(arcId) + "/artifacts").then((d) => {
      artifacts = d;
      const badges = document.getElementById("pipeline-badges");
      if (badges) {
        const stages = [
          { key: "Storyboard", has: true },
          { key: "S1", has: d.task_decomposition },
          { key: "S2", has: d.has_encounters || d.has_opportunities },
          { key: "S3", has: d.feedback },
          { key: "S4", has: d.has_encounters },
          { key: "S5", has: d.expanded_storyboard && d.encounters_json },
        ];
        badges.innerHTML = stages.map((s, i) => {
          const cls = s.has ? "stage has-art" : "stage";
          const arr = i < stages.length - 1 ? "<span class=\"arrow\">→</span>" : "";
          return `<span class="${cls}">${s.key}</span>${arr}`;
        }).join("");
      }
    }).catch(() => {});
  }

  function renderMermaidInto(container, mermaidText, fallbackText) {
    if (!container) return;
    container.innerHTML = "";
    container.classList.remove("mermaid-fallback");
    if (!mermaidText) {
      if (fallbackText) {
        container.textContent = fallbackText;
        container.classList.add("mermaid-fallback");
      }
      return;
    }
    const wrap = document.createElement("div");
    wrap.className = "mermaid";
    wrap.textContent = mermaidText;
    container.appendChild(wrap);
    if (window.mermaid && window.mermaid.run) {
      window.mermaid.run({ nodes: [wrap] }).catch(() => {
        if (!fallbackText) return;
        container.innerHTML = "";
        container.textContent = fallbackText;
        container.classList.add("mermaid-fallback");
      });
    } else if (fallbackText) {
      container.innerHTML = "";
      container.textContent = fallbackText;
      container.classList.add("mermaid-fallback");
    }
  }

  function renderPipelineMermaid() {
    get("/api/diagrams/pipeline_mermaid").then((d) => {
      const mermaidText = d && d.mermaid ? d.mermaid : "";
      renderMermaidInto(document.getElementById("pipeline-strip-mermaid"), mermaidText, "");
      renderMermaidInto(document.getElementById("pipeline-mermaid"), mermaidText, "No diagram available.");
    }).catch(() => {});
  }

  function showTab(name) {
    const current = document.querySelector(".tabs button.active");
    const currentTab = current ? current.dataset.tab : "";
    if (currentTab === "form1" && tdDirty && name !== "form1") {
      if (!confirm("Task decomposition has unsaved changes. Leave?")) return;
    }
    if (currentTab === "form3" && fbDirty && name !== "form3") {
      if (!confirm("Feedback has unsaved changes. Leave?")) return;
    }
    document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
    document.querySelectorAll(".stage-panel").forEach((p) => p.classList.toggle("visible", p.id === "panel-" + name));
    if (name === "session-memory") refreshSessionMemoryFiles();
    if (name === "kb") refreshKbStatus();
  }

  window.addEventListener("beforeunload", (e) => {
    if (tdDirty || fbDirty) e.preventDefault();
  });

  function setKbStatus(text, isErr) {
    const el = document.getElementById("kb-status");
    if (el) { el.textContent = text; el.className = isErr ? "err" : "ok"; }
  }
  function refreshKbStatus() {
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

  function setStatusBadge(id, ok, text) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.classList.toggle("ok", !!ok);
    el.classList.toggle("err", !ok);
  }

  function refreshPrereqs() {
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

  document.querySelectorAll(".tabs button").forEach((b) => {
    b.addEventListener("click", () => showTab(b.dataset.tab));
  });

  document.querySelectorAll(".workspace-tabs button").forEach((b) => {
    b.addEventListener("click", () => showWorkspace(b.dataset.workspace));
  });
  document.querySelectorAll(".right-tabs button").forEach((b) => {
    b.addEventListener("click", () => showRightPanel(b.dataset.right));
  });
  document.querySelectorAll(".bottom-tabs button").forEach((b) => {
    b.addEventListener("click", () => showBottomPanel(b.dataset.bottom));
  });

  const togglePreview = document.getElementById("toggle-preview");
  if (togglePreview) togglePreview.addEventListener("click", () => {
    showPreview = !showPreview;
    renderPreview();
  });
  const saveNote = document.getElementById("save-note");
  if (saveNote) saveNote.addEventListener("click", () => {
    alert("Save is not wired yet. This is a scaffold.");
  });
  const saveCard = document.getElementById("save-card");
  if (saveCard) saveCard.addEventListener("click", () => {
    alert("Save as card is not wired yet.");
  });

  const ragSearch = document.getElementById("rag-search");
  if (ragSearch) ragSearch.addEventListener("click", () => {
    const q = document.getElementById("rag-query");
    const query = (q && q.value || "").trim();
    if (!query) return;
    const outEl = document.getElementById("rag-results");
    if (outEl) outEl.innerHTML = "<p class=\"muted\">Searching…</p>";
    get("/api/kb/search?query=" + encodeURIComponent(query) + "&limit=10")
      .then((d) => {
        if (outEl) outEl.textContent = JSON.stringify(d, null, 2);
      })
      .catch((e) => { if (outEl) outEl.textContent = formatErr(e); });
  });

  const createBtn = document.getElementById("create-module-btn");
  if (createBtn) createBtn.addEventListener("click", () => {
    const campaign = (document.getElementById("create-campaign") && document.getElementById("create-campaign").value || "").trim();
    const moduleNameInput = (document.getElementById("create-module") && document.getElementById("create-module").value || "").trim();
    const scenes = parseInt((document.getElementById("create-scenes") && document.getElementById("create-scenes").value) || "1", 10);
    const npcs = parseInt((document.getElementById("create-npcs") && document.getElementById("create-npcs").value) || "1", 10);
    if (!campaign || !moduleNameInput) {
      setCreateModuleOut("Campaign and module are required.", true);
      return;
    }
    createBtn.disabled = true;
    setCreateModuleOut("Creating module…");
    post("/api/modules/create", {
      campaign_name: campaign,
      module_name: moduleNameInput,
      starting_scene_count: scenes,
      npc_count: npcs
    }).then((d) => {
      setCreateModuleOut(d);
      moduleCampaign = campaign;
      moduleName = moduleNameInput;
      refreshModules();
    }).catch((e) => setCreateModuleOut(formatErr(e), true)).finally(() => { createBtn.disabled = false; });
  });

  ["filter-type", "filter-status", "filter-tags"].forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener("change", refreshModuleTree);
    el.addEventListener("input", refreshModuleTree);
  });

  function refreshSessionMemoryFiles() {
    get("/api/session/files").then((d) => {
      const sel = document.getElementById("session-foreshadow-dropdown");
      if (!sel) return;
      const files = d.files || [];
      sel.innerHTML = "<option value=\"\">(pick from _session_memory or type below)</option>" +
        files.map((f) => `<option value="${escapeHtml(f.path)}">${escapeHtml(f.name)}</option>`).join("");
      sel.onchange = function () {
        const input = document.getElementById("session-foreshadow-path");
        if (input) input.value = sel.value || "";
      };
    }).catch(() => {});
  }

  function out(id, content, isErr) {
    const el = document.getElementById("out-" + id);
    if (!el) return;
    el.innerHTML = "";
    const pre = document.createElement("pre");
    pre.className = isErr ? "err" : "ok";
    pre.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
    el.appendChild(pre);
  }

  document.getElementById("run-s1").addEventListener("click", () => {
    const btn = document.getElementById("run-s1");
    btn.disabled = true;
    out("s1", "Running…");
    post("/api/run/stage1", { arc_id: arcId, storyboard_path: "", output_dir: "" })
      .then((r) => { out("s1", r); refreshTree(); refreshArtifacts(); })
      .catch((e) => out("s1", formatErr(e), true))
      .finally(() => { btn.disabled = false; });
  });
  document.getElementById("run-s2").addEventListener("click", () => {
    const btn = document.getElementById("run-s2");
    btn.disabled = true;
    setProgress("progress-s2", true);
    out("s2", "Running…");
    post("/api/run/stage2", { arc_id: arcId })
      .then((r) => { out("s2", r); refreshTree(); refreshArtifacts(); })
      .catch((e) => out("s2", formatErr(e), true))
      .finally(() => { btn.disabled = false; setProgress("progress-s2", false); });
  });

  document.getElementById("run-s5").addEventListener("click", () => {
    const btn = document.getElementById("run-s5");
    btn.disabled = true;
    out("s5", "Running…");
    post("/api/run/stage5", { arc_id: arcId })
      .then((r) => { out("s5", r); refreshTree(); refreshArtifacts(); })
      .catch((e) => out("s5", formatErr(e), true))
      .finally(() => { btn.disabled = false; });
  });

  function outSessionMemory(data, isErr) {
    const el = document.getElementById("out-session-memory");
    if (!el) return;
    el.innerHTML = "";
    const isError = isErr || (data && data.status === "error");
    const isSkipped = !isError && data && data.status === "skipped";
    let statusClass = "ok";
    if (isError) statusClass = "err";
    else if (isSkipped) statusClass = "warn";
    if (isSkipped && data.reason) {
      const line = document.createElement("p");
      line.className = "warn";
      line.textContent = "Skipped: " + data.reason;
      el.appendChild(line);
    }
    const pre = document.createElement("pre");
    pre.className = statusClass;
    pre.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
    el.appendChild(pre);
    if (!isError && data && data.output_path) {
      const row = document.createElement("p");
      row.className = "muted";
      row.style.marginTop = "0.5em";
      row.appendChild(document.createTextNode("Output: " + data.output_path + " "));
      const copyBtn = document.createElement("button");
      copyBtn.type = "button";
      copyBtn.className = "list-actions";
      copyBtn.textContent = "Copy path";
      copyBtn.style.marginLeft = "0.5em";
      copyBtn.onclick = function () {
        navigator.clipboard.writeText(data.output_path).then(() => {
          copyBtn.textContent = "Copied";
          setTimeout(() => { copyBtn.textContent = "Copy path"; }, 1500);
        }).catch(() => {});
      };
      row.appendChild(copyBtn);
      const filename = data.output_path.replace(/\\/g, "/").split("/").pop();
      if (filename && data.output_path.indexOf("_session_memory") !== -1) {
        const viewLink = document.createElement("a");
        viewLink.href = "/api/session/file/" + encodeURIComponent(filename);
        viewLink.target = "_blank";
        viewLink.rel = "noopener";
        viewLink.textContent = "View output";
        viewLink.style.marginLeft = "0.5em";
        row.appendChild(viewLink);
      }
      el.appendChild(row);
    }
  }

  document.getElementById("run-archivist").addEventListener("click", function () {
    const sessionPath = document.getElementById("session-archivist-path").value.trim();
    if (!sessionPath) { outSessionMemory("Enter a session note path.", true); return; }
    this.disabled = true;
    setProgress("progress-session", true);
    const outEl = document.getElementById("out-session-memory");
    if (outEl) outEl.innerHTML = "<p class=\"muted\">Running…</p>";
    post("/api/session/archivist", { session_path: sessionPath })
      .then((r) => {
        outSessionMemory(r);
        if (r && r.status === "success" && r.output_path) {
          const foreshadowInput = document.getElementById("session-foreshadow-path");
          if (foreshadowInput) foreshadowInput.value = r.output_path;
        }
      })
      .catch((e) => outSessionMemory(formatErr(e), true))
      .finally(() => { this.disabled = false; setProgress("progress-session", false); });
  });

  document.getElementById("run-foreshadow").addEventListener("click", function () {
    const contextPath = document.getElementById("session-foreshadow-path").value.trim();
    if (!contextPath) { outSessionMemory("Enter a context file path (Archivist output or session summary).", true); return; }
    this.disabled = true;
    setProgress("progress-session", true);
    const outEl = document.getElementById("out-session-memory");
    if (outEl) outEl.innerHTML = "<p class=\"muted\">Running…</p>";
    post("/api/session/foreshadow", { context_path: contextPath })
      .then((r) => outSessionMemory(r))
      .catch((e) => outSessionMemory(formatErr(e), true))
      .finally(() => { this.disabled = false; setProgress("progress-session", false); });
  });

  function refreshS4Drafts() {
    get("/api/arc/" + encodeURIComponent(arcId) + "/tree").then((d) => {
      const paths = (d.encounters || []).concat(d.opportunities || []).map((e) => e.path);
      const sel = document.getElementById("s4-draft");
      sel.innerHTML = "<option value=\"\">(select draft)</option>" + paths.map((p) => `<option value="${escapeHtml(p)}">${escapeHtml(p.split(/[/\\]/).pop())}</option>`).join("");
    }).catch(() => {});
  }

  document.getElementById("run-s4").addEventListener("click", function () {
    const draftPath = document.getElementById("s4-draft").value;
    if (!draftPath) { out("s4", "Select a draft first.", true); return; }
    this.disabled = true;
    setProgress("progress-s4", true);
    out("s4", "Running…");
    post("/api/run/stage4", { draft_path: draftPath, arc_id: arcId })
      .then((r) => { out("s4", r); if (r.status === "success") { refreshTree(); refreshArtifacts(); refreshS4Drafts(); } })
      .catch((e) => out("s4", formatErr(e), true))
      .finally(() => { this.disabled = false; setProgress("progress-s4", false); });
  });

  function refreshTaskDecompForm() {
    get("/api/arc/" + encodeURIComponent(arcId) + "/task_decomposition").then((data) => {
      const local = loadLocalDraft("td");
      if (local && local.data && confirm("Restore unsaved Task Decomp draft?")) {
        renderTaskDecompForm(local.data);
        tdDirty = true;
      } else {
        renderTaskDecompForm(data);
        tdDirty = false;
      }
    }).catch(() => {
      const local = loadLocalDraft("td");
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
  const panelForm1 = document.getElementById("panel-form1");
  if (panelForm1) panelForm1.addEventListener("input", () => {
    tdDirty = true;
    const draft = collectTaskDecomp();
    if (draft) saveLocalDraft("td", draft);
  });
  if (panelForm1) panelForm1.addEventListener("change", () => {
    tdDirty = true;
    const draft = collectTaskDecomp();
    if (draft) saveLocalDraft("td", draft);
  });
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
    refreshTaskDecompForm();
  }

  document.getElementById("td-add-enc").addEventListener("click", () => {
    const d = window._tdData || { arc_id: arcId, encounters: [], opportunities: [], sequence_constraints: [] };
    d.encounters = d.encounters || [];
    d.encounters.push({ id: "enc_" + d.encounters.length, name: "", type: "combat", sequence: d.encounters.length + 1, storyboard_section: "", after: null, before: null });
    window._tdData = d;
    refreshTaskDecompForm();
  });
  document.getElementById("td-add-opp").addEventListener("click", () => {
    const d = window._tdData || { arc_id: arcId, encounters: [], opportunities: [], sequence_constraints: [] };
    d.opportunities = d.opportunities || [];
    d.opportunities.push({ id: "opp_" + d.opportunities.length, name: "", type: "social", sequence: 1, optional: true, storyboard_section: "", note: "" });
    window._tdData = d;
    refreshTaskDecompForm();
  });
  document.getElementById("td-add-constraint").addEventListener("click", () => {
    const d = window._tdData || { arc_id: arcId, encounters: [], opportunities: [], sequence_constraints: [] };
    d.sequence_constraints = d.sequence_constraints || [];
    d.sequence_constraints.push("");
    window._tdData = d;
    refreshTaskDecompForm();
  });

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
    d.arc_id = document.getElementById("td-arc-id").value || arcId;
    d.storyboard_ref = document.getElementById("td-storyboard-ref").value;
    return d;
  }

  document.getElementById("save-td").addEventListener("click", () => {
    const d = collectTaskDecomp();
    if (!d) { setValidationErrors("td-errors", ["arc_id is required."]); return; }
    const errs = validateTaskDecomp(d);
    setValidationErrors("td-errors", errs);
    if (errs.length) return;
    put("/api/arc/" + encodeURIComponent(arcId) + "/task_decomposition", d)
      .then((r) => {
        tdDirty = false;
        clearLocalDraft("td");
        alert("Saved: " + (r.path || r.status));
      })
      .catch((e) => showFileModal("Error", formatErr(e), "", true));
  });

  function refreshFeedbackForm() {
    get("/api/arc/" + encodeURIComponent(arcId) + "/feedback").then((data) => {
      const local = loadLocalDraft("fb");
      if (local && local.data && confirm("Restore unsaved Feedback draft?")) {
        renderFeedbackForm(local.data);
        fbDirty = true;
      } else {
        renderFeedbackForm(data);
        fbDirty = false;
      }
    }).catch(() => {
      const local = loadLocalDraft("fb");
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
    window._fbData = data;
  }
  const panelForm3 = document.getElementById("panel-form3");
  if (panelForm3) panelForm3.addEventListener("input", () => {
    fbDirty = true;
    const draft = collectFeedback();
    if (draft) saveLocalDraft("fb", draft);
  });
  if (panelForm3) panelForm3.addEventListener("change", () => {
    fbDirty = true;
    const draft = collectFeedback();
    if (draft) saveLocalDraft("fb", draft);
  });
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
      link_npc: () => `<input placeholder="npc_id" value="${escapeHtml(it.npc_id || "")}" data-f="npc_id" /><input placeholder="instruction" value="${escapeHtml(it.instruction || "")}" data-f="instruction" />`,
      link_location: () => `<input placeholder="location_id" value="${escapeHtml(it.location_id || "")}" data-f="location_id" /><input placeholder="instruction" value="${escapeHtml(it.instruction || "")}" data-f="instruction" />`,
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
    refreshFeedbackForm();
  }

  document.getElementById("fb-add").addEventListener("click", () => {
    const d = window._fbData || { arc_id: arcId, encounters: [] };
    const encId = document.getElementById("fb-encounter").value;
    if (!encId) { alert("Select an encounter first."); return; }
    let enc = (d.encounters || []).find((e) => e.id === encId);
    if (!enc) { enc = { id: encId, feedback: [] }; d.encounters = d.encounters || []; d.encounters.push(enc); }
    enc.feedback = enc.feedback || [];
    enc.feedback.push({ type: "other", instruction: "" });
    window._fbData = d;
    refreshFeedbackForm();
  });
  function collectFeedback() {
    const d = window._fbData || { arc_id: arcId, encounters: [] };
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
    d.arc_id = arcId;
    return d;
  }

  document.getElementById("save-fb").addEventListener("click", () => {
    const d = collectFeedback();
    if (!d) { setValidationErrors("fb-errors", ["Select an encounter first."]); return; }
    const errs = validateFeedback(d);
    setValidationErrors("fb-errors", errs);
    if (errs.length) return;
    put("/api/arc/" + encodeURIComponent(arcId) + "/feedback", d)
      .then((r) => {
        fbDirty = false;
        clearLocalDraft("fb");
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
  });

  const fileModalClose = document.getElementById("file-modal-close");
  if (fileModalClose) fileModalClose.addEventListener("click", closeFileModal);
  const fileModalBackdrop = document.getElementById("file-modal-backdrop");
  if (fileModalBackdrop) fileModalBackdrop.addEventListener("click", closeFileModal);

  refreshArcs();
  setArc(arcId);
  showTab("s1");
  showWorkspace("workbench");
  showRightPanel("chat");
  showBottomPanel("timeline");
  refreshModules();
  renderPipelineMermaid();
  refreshPrereqs();
})();
