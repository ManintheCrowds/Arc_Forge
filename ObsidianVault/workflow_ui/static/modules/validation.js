// PURPOSE: Client-side validation for task_decomposition and feedback.
// DEPENDENCIES: none
// MODIFICATION NOTES: Extracted from monolithic app.js (Wave C modularization).

export const FEEDBACK_TYPES = ["expand", "change", "add_mechanic", "remove", "link_npc", "link_location", "other"];
export const ENCOUNTER_TYPES = ["combat", "social", "exploration", "environmental"];

export function validateTaskDecomp(data) {
  const errors = [];
  if (!data.arc_id) errors.push("arc_id is required.");
  const encs = data.encounters || [];
  encs.forEach((e, i) => {
    if (!e.id) errors.push(`encounters[${i}].id is required.`);
    if (!e.name) errors.push(`encounters[${i}].name is required.`);
    if (!e.type) errors.push(`encounters[${i}].type is required.`);
    if (e.type && ENCOUNTER_TYPES.indexOf(e.type) === -1) {
      errors.push(`encounters[${i}].type must be one of: ${ENCOUNTER_TYPES.join(", ")}`);
    }
    if (e.sequence == null || Number.isNaN(Number(e.sequence))) {
      errors.push(`encounters[${i}].sequence must be a number.`);
    }
  });
  const opps = data.opportunities || [];
  opps.forEach((o, i) => {
    if (!o.id) errors.push(`opportunities[${i}].id is required.`);
    if (!o.name) errors.push(`opportunities[${i}].name is required.`);
    if (!o.type) errors.push(`opportunities[${i}].type is required.`);
    if (o.type && ENCOUNTER_TYPES.indexOf(o.type) === -1) {
      errors.push(`opportunities[${i}].type must be one of: ${ENCOUNTER_TYPES.join(", ")}`);
    }
    if (o.sequence == null || Number.isNaN(Number(o.sequence))) {
      errors.push(`opportunities[${i}].sequence must be a number.`);
    }
  });
  return errors;
}

export function validateFeedback(data) {
  const errors = [];
  if (!data.arc_id) errors.push("arc_id is required.");
  const encs = data.encounters || [];
  encs.forEach((enc, i) => {
    if (!enc.id) errors.push(`encounters[${i}].id is required.`);
    const items = enc.feedback || [];
    items.forEach((it, j) => {
      const base = `encounters[${i}].feedback[${j}]`;
      if (!it.type) errors.push(`${base}.type is required.`);
      if (it.type && FEEDBACK_TYPES.indexOf(it.type) === -1) {
        errors.push(`${base}.type must be one of: ${FEEDBACK_TYPES.join(", ")}`);
      }
      const has = (k) => it[k] != null && String(it[k]).trim() !== "";
      if (it.type === "expand" && !(has("target") && has("instruction"))) {
        errors.push(`${base} requires target and instruction.`);
      } else if (it.type === "change" && !(has("target") && (has("to") || has("instruction")))) {
        errors.push(`${base} requires target and to (or instruction).`);
      } else if (it.type === "add_mechanic" && !has("detail")) {
        errors.push(`${base} requires detail.`);
      } else if (it.type === "remove" && !(has("target") || has("instruction"))) {
        errors.push(`${base} requires target or instruction.`);
      } else if (it.type === "link_npc" && !(has("npc_id") && has("instruction"))) {
        errors.push(`${base} requires npc_id and instruction.`);
      } else if (it.type === "link_location" && !(has("location_id") && has("instruction"))) {
        errors.push(`${base} requires location_id and instruction.`);
      } else if (it.type === "other" && !(has("instruction") || has("detail"))) {
        errors.push(`${base} requires instruction or detail.`);
      }
    });
  });
  return errors;
}
