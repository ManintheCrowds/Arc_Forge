// PURPOSE: API helpers for workflow_ui.
// DEPENDENCIES: fetch
// MODIFICATION NOTES: Extracted from monolithic app.js (Wave C modularization).

const API = "";

export function get(url) {
  return fetch(API + url).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
}

export function post(url, body) {
  return fetch(API + url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
}

export function put(url, body) {
  return fetch(API + url, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
}
