// PURPOSE: LocalStorage draft persistence helpers.
// DEPENDENCIES: localStorage
// MODIFICATION NOTES: Extracted from monolithic app.js (Wave C modularization).

export function loadLocalDraft(kind, arcId) {
  try {
    const raw = localStorage.getItem(`workflow_ui:${kind}:draft:${arcId}`);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function saveLocalDraft(kind, arcId, data) {
  try {
    localStorage.setItem(
      `workflow_ui:${kind}:draft:${arcId}`,
      JSON.stringify({ savedAt: Date.now(), data: data })
    );
  } catch (e) {}
}

export function clearLocalDraft(kind, arcId) {
  try {
    localStorage.removeItem(`workflow_ui:${kind}:draft:${arcId}`);
  } catch (e) {}
}
