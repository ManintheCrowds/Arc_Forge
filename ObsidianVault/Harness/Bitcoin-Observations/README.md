---
title: "Bitcoin Observations Log"
tags: ["type/harness-bitcoin-obs", "status/mirror", "domain/bitcoin"]
group: harness-bitcoin
color: rose
cssclasses:
  - vault-grp-harness-bitcoin
  - vault-col-rose
---

# Bitcoin Observations Log

Structured observation logs for Bitcoin-Chaos convergence. One file per day: `YYYY-MM-DD_observations.md`.

## Schema (per entry)

| Field | Type | Description |
|-------|------|--------------|
| timestamp | ISO8601 | When observed |
| source | string | e.g. mempool.space, GitHub, Fedimint docs |
| type | enum | `design_decision` \| `failure_mode` \| `community_norm` |
| content | string | Observation text |

## Entry format

```markdown
### YYYY-MM-DDTHH:MM:SSZ | source | type
Content here.
```

## Usage

- **Primary:** Agent uses `observation_log_append(content, source, obs_type, date?)` MCP tool (see [BITCOIN_AGENT_CAPABILITIES.md](../BITCOIN_AGENT_CAPABILITIES.md)).
- **Fallback:** read `docs/bitcoin_observations/YYYY-MM-DD_observations.md`, append entry, write back.
- See [BITCOIN_OBSERVATION_TEMPLATE.md](../BITCOIN_OBSERVATION_TEMPLATE.md) for full template.

## Research MOC (agents, Ghost, OpenClaw)

- **Voelbel / ClawHub / Ghost / SCP primer:** [joseph-voelbel-openclaw-clawhub.md](../collaborators/joseph-voelbel-openclaw-clawhub.md) — catalog, integration order, Cursor vs OpenClaw skills.
- **Cursor + OpenClaw integration (repo stance):** [CURSOR_OPENCLAW_INTEGRATION.md](../collaborators/CURSOR_OPENCLAW_INTEGRATION.md).
- **PKM without OpenClaw (attention pockets, graph):** [PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md](../PKM_ATTENTION_POCKETS_AND_BRAIN_MAP.md).
- **Ghost runbook (GHOST1):** [GHOST1_RUNBOOK.md](../GHOST1_RUNBOOK.md).
- **Seminar index (BitDevs 36):** [2026-03-10-bitdevs-mpls-seminar-36.md](2026-03-10-bitdevs-mpls-seminar-36.md) (includes §9 Voelbel case study).
