---
title: "Alienware Graphics Amplifier — GPU upgrade archive"
tags: ["type/harness-doc", "status/mirror", "domain/harness"]
group: harness-docs
color: blue
cssclasses:
  - vault-grp-harness-docs
  - vault-col-blue
---

# Alienware Graphics Amplifier — GPU upgrade archive

**Archived:** 2026-04-09  
**Scope:** local-proto — Alpha R2 + AGA alternate topology; complements [HARDWARE.md](HARDWARE.md) and [ALPHA_R2_AGA_SETUP.md](ALPHA_R2_AGA_SETUP.md).

**Primary Dell reference:** [Alienware Graphics Amplifier — compatibility, supported cards](https://www.dell.com/support/kbdoc/en-us/000178406/alienware-graphics-amplifier-supported-graphics-card-list) (KB **000178406**, last modified 2026-01-22 per article).

---

## Why this doc exists

Condensed, repo-local record of which GPUs Dell lists for the AGA, physical limits, and practical picks for **local inference** (Ollama, OpenClaw) so you do not have to re-derive from chat history.

---

## Officially supported systems (excerpt)

Per Dell KB: Alienware 13/15/17 (multiple R gens), Alpha R2, X51 R3, Area-51m variants, M15/M17 variants, etc. Confirm your exact model on the KB if needed.

---

## Physical and electrical limits (AGA)

From Dell KB:

- **Form factor:** Full-length **dual-slot** cards, recommended up to **~10.5"**.
- **Envelope:** Roughly **267 mm × 112 mm × 40 mm** (standard double-wide PCIe-style).
- **Power:** PSU supports up to **~385 W** for the graphics card.
- **Caveat:** Many **non-reference** boards (oversized heatsinks, some **OC / dual- / triple-fan** retail cards) may **not fit** or hit **VBIOS** compatibility issues. **Reference / Founders Edition**–class boards are the safest fit.

---

## NVIDIA — supported list (strongest first)

Highest tier on Dell’s list is **Turing RTX**, then Pascal, Maxwell, etc. For **CUDA / Ollama**, prefer NVIDIA unless you standardize on ROCm.

**Top of list (performance):**

- GeForce **RTX 2080 Ti**
- GeForce **RTX 2080**, **RTX 2070**

**Still strong (Pascal):**

- **GTX 1080 Ti**, **GTX 1080**, **GTX 1070 Ti**, **GTX 1070**, down through **GTX 1060**, **GTX 980** series, older GTX 700/600 series (see KB for full enumeration).

---

## AMD — supported list (summary)

Peak on the list is **Polaris / older GCN** (e.g. **RX 580**, **RX 570**, **RX 480**, R9 / HD 7000 series per KB). Fine for general use; for this stack’s default **CUDA** path, NVIDIA is usually simpler.

---

## Ideal model choice (within Dell’s published list)

| Goal | Pick |
|------|------|
| **Best overall on the KB list** | **RTX 2080 Ti** (reference-sized board). Strongest GPU Dell lists; **11 GB VRAM** helps **7B–13B** quantized workloads vs 8 GB cards. |
| **Balance cost / power / fit** | **RTX 2070** or **RTX 2080** (8 GB), reference-style cooler. |
| **VRAM on a budget (used)** | **GTX 1080 Ti** (**11 GB**) — older arch than Turing; still VRAM-competitive for size-class inference. |
| **AMD only** | **RX 580** (top of AMD list here) — weigh vs CUDA tooling preferences. |

**Not on Dell’s list:** RTX 30/40 series and newer — community may run them, but **Dell does not certify** them; fit, power, and behavior are operator risk.

---

## Tie-in: local-proto inference envelope

- **More VRAM** → larger quants / headroom for **7B–13B** classes (always re-measure with `nvidia-smi` and `ollama ps`).
- After upgrade, repeat the **tools probe** and readiness steps in [OPENCLAW_READINESS.md](OPENCLAW_READINESS.md) and sizing tables in [HARDWARE.md](HARDWARE.md).

---

## Private copy and Obsidian

| Path | Role |
|------|------|
| **This file** | Canonical copy under `local-proto/docs/` (version control if the repo commits it). |
| **`local-proto/docs/private/`** | **Gitignored** optional folder — copy or symlink this note here if you want a non-committed duplicate beside other operator-only notes. |
| **Obsidian vault** | Run [sync_harness_to_vault.ps1](../scripts/sync_harness_to_vault.ps1) with `OBSIDIAN_VAULT_ROOT` set; this doc is copied to **`Harness/Docs/AGA-GPU-Upgrade-Archive.md`** for review in Obsidian (same pattern as other harness docs). |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-09 | Initial archive from AGA compatibility analysis + Dell KB 000178406. |
