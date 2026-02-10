// PURPOSE: Stage run button handlers (S1, S2, S4, S5).
// DEPENDENCIES: api.js, utils.js, pipeline.js, forms.js, state.js
// MODIFICATION NOTES: Extracted from app.js.

import { post } from "./api.js";
import { formatErr, setProgress } from "./utils.js";
import { refreshArtifacts } from "./pipeline.js";
import { refreshS4Drafts } from "./forms.js";
import { refreshTree } from "./files.js";
import { getArcId } from "./state.js";

function out(id, content, isErr) {
  const el = document.getElementById("out-" + id);
  if (!el) return;
  el.innerHTML = "";
  const pre = document.createElement("pre");
  pre.className = isErr ? "err" : "ok";
  pre.textContent = typeof content === "string" ? content : JSON.stringify(content, null, 2);
  el.appendChild(pre);
}

export function initStageHandlers() {
  document.getElementById("run-s1").addEventListener("click", () => {
    const btn = document.getElementById("run-s1");
    btn.disabled = true;
    out("s1", "Running…");
    post("/api/run/stage1", { arc_id: getArcId(), storyboard_path: "", output_dir: "" })
      .then((r) => { out("s1", r); refreshTree(); refreshArtifacts(getArcId()); })
      .catch((e) => out("s1", formatErr(e), true))
      .finally(() => { btn.disabled = false; });
  });
  document.getElementById("run-s2").addEventListener("click", () => {
    const btn = document.getElementById("run-s2");
    btn.disabled = true;
    setProgress("progress-s2", true);
    out("s2", "Running…");
    post("/api/run/stage2", { arc_id: getArcId() })
      .then((r) => { out("s2", r); refreshTree(); refreshArtifacts(getArcId()); })
      .catch((e) => out("s2", formatErr(e), true))
      .finally(() => { btn.disabled = false; setProgress("progress-s2", false); });
  });

  document.getElementById("run-s5").addEventListener("click", () => {
    const btn = document.getElementById("run-s5");
    btn.disabled = true;
    out("s5", "Running…");
    post("/api/run/stage5", { arc_id: getArcId() })
      .then((r) => { out("s5", r); refreshTree(); refreshArtifacts(getArcId()); })
      .catch((e) => out("s5", formatErr(e), true))
      .finally(() => { btn.disabled = false; });
  });

  document.getElementById("run-s4").addEventListener("click", function () {
    const draftPath = document.getElementById("s4-draft").value;
    if (!draftPath) { out("s4", "Select a draft first.", true); return; }
    this.disabled = true;
    setProgress("progress-s4", true);
    out("s4", "Running…");
    post("/api/run/stage4", { draft_path: draftPath, arc_id: getArcId() })
      .then((r) => { out("s4", r); if (r.status === "success") { refreshTree(); refreshArtifacts(getArcId()); refreshS4Drafts(); } })
      .catch((e) => out("s4", formatErr(e), true))
      .finally(() => { this.disabled = false; setProgress("progress-s4", false); });
  });
}
