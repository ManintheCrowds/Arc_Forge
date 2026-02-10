// PURPOSE: File viewer modal behavior.
// DEPENDENCIES: DOM
// MODIFICATION NOTES: Extracted from app.js.

export function showFileModal(title, content, note, isErr) {
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

export function closeFileModal() {
  const modal = document.getElementById("file-modal");
  if (modal) {
    modal.classList.remove("visible");
    modal.classList.remove("is-error");
  }
}

export function initModalHandlers() {
  const fileModalClose = document.getElementById("file-modal-close");
  if (fileModalClose) fileModalClose.addEventListener("click", closeFileModal);
  const fileModalBackdrop = document.getElementById("file-modal-backdrop");
  if (fileModalBackdrop) fileModalBackdrop.addEventListener("click", closeFileModal);
}
