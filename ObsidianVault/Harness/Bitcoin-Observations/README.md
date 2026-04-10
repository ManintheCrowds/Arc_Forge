---
title: "Bitcoin Observations Log"
tags: ["type/harness-bitcoin-obs", "status/mirror", "domain/bitcoin"]
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
