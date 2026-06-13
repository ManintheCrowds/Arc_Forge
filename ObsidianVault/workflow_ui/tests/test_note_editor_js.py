import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest


MODULE_DIR = Path(__file__).resolve().parents[1] / "static" / "modules"

NODE_HARNESS = """
class Element {
  constructor(id) {
    this.id = id;
    this.value = "";
    this.placeholder = "";
    this.textContent = "";
    this.className = "";
    this.innerHTML = "";
    this.style = { display: "" };
    this.attributes = {};
    this.listeners = {};
  }

  addEventListener(type, callback) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(callback);
  }

  dispatch(type, event = {}) {
    for (const callback of this.listeners[type] || []) {
      callback({ target: this, ...event });
    }
  }

  setAttribute(name, value) {
    this.attributes[name] = value;
  }

  getAttribute(name) {
    return this.attributes[name];
  }
}

const elements = {
  "module-campaign": new Element("module-campaign"),
  "note-editor": new Element("note-editor"),
  "note-preview": new Element("note-preview"),
  "save-note": new Element("save-note"),
  "save-card": new Element("save-card"),
  "toggle-preview": new Element("toggle-preview"),
  "note-editor-out": new Element("note-editor-out"),
};
elements["module-campaign"].value = "first_arc";

globalThis.document = {
  body: new Element("body"),
  getElementById(id) {
    return elements[id] || null;
  },
};

globalThis.window = {
  listeners: {},
  confirm() {
    return true;
  },
  addEventListener(type, callback) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(callback);
  },
  dispatchEvent(event) {
    for (const callback of this.listeners[event.type] || []) {
      callback(event);
    }
  },
};

const calls = [];
const pendingLoads = new Map();
const pendingSaves = new Map();
let manualLoads = false;
let manualSaves = false;

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function okText(text) {
  return {
    ok: true,
    text: async () => text,
    json: async () => ({ status: "ok" }),
  };
}

function notFound() {
  return {
    ok: false,
    status: 404,
    statusText: "Not Found",
    json: async () => ({ error: "not_found" }),
  };
}

globalThis.fetch = (url, options = {}) => {
  calls.push({ url, options });
  if (options.method === "PUT") {
    if (manualSaves) {
      return new Promise((resolve) => {
        pendingSaves.set(url, resolve);
      });
    }
    return Promise.resolve({
      ok: true,
      json: async () => ({ status: "saved" }),
    });
  }
  if (manualLoads) {
    return new Promise((resolve) => {
      pendingLoads.set(url, resolve);
    });
  }
  if (url.includes("missing")) {
    return Promise.resolve(notFound());
  }
  return Promise.resolve(okText("Loaded: " + url));
};

const module = await import("./note_editor.js");
module.initNoteEditor();

const editor = elements["note-editor"];

async function flush() {
  await Promise.resolve();
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
}

async function selectNote(path) {
  window.dispatchEvent({ type: "workbench:tree-select", detail: { path } });
  await flush();
}

function changeCampaign(campaign) {
  elements["module-campaign"].value = campaign;
  elements["module-campaign"].dispatch("change");
}

function clickSave() {
  elements["save-note"].dispatch("click");
}

function putCalls() {
  return calls.filter((call) => call.options && call.options.method === "PUT");
}

__CASE_BODY__
"""


def _run_note_editor_case(tmp_path, case_body):
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required for note_editor.js module tests")

    module_tmp = tmp_path / "modules"
    module_tmp.mkdir()
    shutil.copy2(MODULE_DIR / "note_editor.js", module_tmp / "note_editor.js")
    shutil.copy2(MODULE_DIR / "utils.js", module_tmp / "utils.js")
    (module_tmp / "package.json").write_text('{"type":"module"}\n', encoding="utf-8")
    (module_tmp / "runner.mjs").write_text(
        NODE_HARNESS.replace("__CASE_BODY__", textwrap.dedent(case_body)),
        encoding="utf-8",
    )

    result = subprocess.run(
        [node, "runner.mjs"],
        cwd=module_tmp,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_campaign_change_clears_save_target(tmp_path):
    _run_note_editor_case(
        tmp_path,
        """
        await selectNote("first_arc/scene.md");
        editor.value = "edited scene";
        editor.dispatch("input");
        changeCampaign("second_arc");
        clickSave();
        await flush();

        assert(putCalls().length === 0, "campaign changes must clear the loaded save target");
        assert(document.body.getAttribute("data-active-note-path") === "", "active note path should be cleared");
        """,
    )


def test_failed_load_cannot_be_saved_as_empty_file(tmp_path):
    _run_note_editor_case(
        tmp_path,
        """
        await selectNote("first_arc/missing.md");
        clickSave();
        await flush();

        assert(putCalls().length === 0, "failed loads must not leave a saveable subpath");
        assert(document.body.getAttribute("data-active-note-path") === "", "failed loads should clear active note context");
        """,
    )


def test_stale_load_response_does_not_replace_current_note(tmp_path):
    _run_note_editor_case(
        tmp_path,
        """
        manualLoads = true;
        const firstLoad = selectNote("first_arc/a.md");
        const firstUrl = "/api/arc/first_arc/file/a.md";
        assert(pendingLoads.has(firstUrl), "first note load should be pending");

        const secondLoad = selectNote("first_arc/b.md");
        const secondUrl = "/api/arc/first_arc/file/b.md";
        assert(pendingLoads.has(secondUrl), "second note load should be pending");

        pendingLoads.get(secondUrl)(okText("B content"));
        await secondLoad;
        assert(editor.value === "B content", "second note should load first");

        pendingLoads.get(firstUrl)(okText("A content"));
        await firstLoad;
        await flush();
        assert(editor.value === "B content", "stale first response must be ignored");

        clickSave();
        await flush();
        const puts = putCalls();
        assert(puts.length === 1, "current note should be saved once");
        assert(puts[0].url === "/api/arc/first_arc/file/b.md", "save should target current note path");
        assert(puts[0].options.body === "B content", "save should use current note content");
        """,
    )


def test_stale_save_response_cannot_enable_loading_note_save(tmp_path):
    _run_note_editor_case(
        tmp_path,
        """
        manualSaves = true;
        await selectNote("first_arc/a.md");
        editor.value = "A edited";
        editor.dispatch("input");
        clickSave();

        const saveUrl = "/api/arc/first_arc/file/a.md";
        assert(pendingSaves.has(saveUrl), "first note save should be pending");

        manualLoads = true;
        const secondLoad = selectNote("first_arc/b.md");
        const secondUrl = "/api/arc/first_arc/file/b.md";
        assert(pendingLoads.has(secondUrl), "second note load should be pending");

        pendingSaves.get(saveUrl)({
          ok: true,
          json: async () => ({ status: "saved" }),
        });
        await flush();

        clickSave();
        await flush();
        assert(putCalls().length === 1, "stale save completion must not enable the loading note");

        pendingLoads.get(secondUrl)(okText("B content"));
        await secondLoad;
        await flush();
        clickSave();
        await flush();

        const puts = putCalls();
        assert(puts.length === 2, "loaded second note should save after its GET resolves");
        assert(puts[1].url === secondUrl, "second save should target loaded second note");
        assert(puts[1].options.body === "B content", "second save should use loaded second note content");
        """,
    )
