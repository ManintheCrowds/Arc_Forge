// PURPOSE: Workbench workflow graph (Mermaid), node selection, Run selected node → stage APIs.
// DEPENDENCIES: api.js, pipeline.js, utils.js
// MODIFICATION NOTES: Phase 3 Workflow panel.

import { get, post } from "./api.js";
import { formatErr } from "./utils.js";
import { renderMermaidInto } from "./pipeline.js";
import { refreshArtifacts } from "./pipeline.js";
import { refreshTree } from "./files.js";

const WORKFLOW_MERMAID = `flowchart LR
  brainstorm[Brainstorm]
  outline[Outline]
  scenedraft[SceneDraft]
  npcs[NPCs]
  review[Review]
  export[Export]
  brainstorm --> outline --> scenedraft --> npcs --> review --> export
  click brainstorm call workflowSelect("brainstorm")
  click outline call workflowSelect("outline")
  click scenedraft call workflowSelect("scenedraft")
  click npcs call workflowSelect("npcs")
  click review call workflowSelect("review")
  click export call workflowSelect("export")`;

const NODE_TO_STAGE = {
  brainstorm: "stage1",
  outline: "stage1",
  scenedraft: "stage2",
  npcs: "stage2",
  review: "stage4",
  export: "stage5",
};

let selectedNode = null;

function getWorkbenchCampaign() {
  const el = document.getElementById("module-campaign");
  return (el && el.value) || "first_arc";
}

function setRunButtonState() {
  const btn = document.getElementById("run-workflow-node");
  if (!btn) return;
  btn.disabled = !selectedNode;
  if (selectedNode) {
    btn.textContent = `Run ${selectedNode}`;
  } else {
    btn.textContent = "Run selected node";
  }
}

function selectNode(nodeId) {
  selectedNode = nodeId;
  setRunButtonState();
}

export function workflowSelect(nodeId) {
  if (NODE_TO_STAGE[nodeId]) selectNode(nodeId);
}

function renderWorkflowGraph() {
  window.workflowSelect = workflowSelect;
  const container = document.getElementById("workflow-graph");
  if (!container) return;
  renderMermaidInto(container, WORKFLOW_MERMAID, "Brainstorm → Outline → SceneDraft → NPCs → Review → Export");
}

async function runStage4(arcId) {
  const tree = await get("/api/arc/" + encodeURIComponent(arcId) + "/tree");
  const paths = (tree.encounters || []).concat(tree.opportunities || []).map((e) => e.path);
  const draftPath = paths[0];
  if (!draftPath) {
    throw new Error("No draft found. Run S2 first to generate encounter drafts.");
  }
  return post("/api/run/stage4", { draft_path: draftPath, arc_id: arcId });
}

async function runStage(nodeId) {
  const stage = NODE_TO_STAGE[nodeId];
  const arcId = getWorkbenchCampaign();
  const body = { arc_id: arcId };
  if (stage === "stage1") {
    return post("/api/run/stage1", body);
  }
  if (stage === "stage2") {
    return post("/api/run/stage2", body);
  }
  if (stage === "stage4") {
    return runStage4(arcId);
  }
  if (stage === "stage5") {
    return post("/api/run/stage5", body);
  }
  throw new Error("Unknown stage");
}

export function initWorkflow() {
  const runBtn = document.getElementById("run-workflow-node");
  const feedbackEl = document.getElementById("workflow-run-out");
  if (!runBtn) return;

  runBtn.addEventListener("click", () => {
    if (!selectedNode) return;
    runBtn.disabled = true;
    const show = (msg, err) => {
      if (feedbackEl) {
        feedbackEl.textContent = msg;
        feedbackEl.className = "out " + (err ? "err" : "ok");
      }
    };
    runStage(selectedNode)
      .then((r) => {
        show(typeof r === "string" ? r : (r.status || JSON.stringify(r)));
        refreshTree();
        refreshArtifacts(getWorkbenchCampaign());
        window.dispatchEvent(new CustomEvent("workbench:refresh"));
        selectNode(null);
      })
      .catch((e) => show(formatErr(e), true))
      .finally(() => { runBtn.disabled = false; });
  });

  renderWorkflowGraph();
  setRunButtonState();
}
