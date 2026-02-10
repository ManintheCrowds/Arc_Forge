// PURPOSE: Shared mutable UI state.
// DEPENDENCIES: none
// MODIFICATION NOTES: Introduced for Wave C modularization.

let arcId = "first_arc";
let artifacts = {};

export function getArcId() {
  return arcId;
}

export function setArcId(id) {
  arcId = id || "first_arc";
}

export function getArtifacts() {
  return artifacts;
}

export function setArtifacts(data) {
  artifacts = data || {};
}
