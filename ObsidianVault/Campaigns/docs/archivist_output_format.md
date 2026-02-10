# Archivist Output Format

**Source:** [narrative_workbench_spec.md](narrative_workbench_spec.md) § IV.A. Defines the structure of Archivist LLM output so scripts can parse or append it.

---

## Canonical timeline entries

- One bullet or structured line per event.
- Each entry: **session ref** (e.g. date or session id) + **one-line description**.
- Example:
  - `2025-01-15 | PCs confronted the smuggler at the depot; one casualty.`
  - `Session 3 | Negotiation with Ork boss failed; combat ensued.`

---

## Flagged future consequences

- Short list of consequences the Archivist infers from the session.
- Optional per item: **probability** (e.g. high/medium/low or %) and **time horizon** (e.g. 2–3 sessions).
- Example:
  - `Smuggler faction will seek retaliation (high; 1–2 sessions).`
  - `Ork truce may collapse if PCs return to sector (medium; 2–5 sessions).`

---

## Retrieval anchors

- Tags or keys for RAG/lookup: **faction**, **location**, **NPC**, **thread id**.
- Used to target retrieval when drafting later sessions.
- Example:
  - `faction: smugglers, orks | location: depot, sector 7 | NPC: Vorlag, Grendel | thread: depot_incident`

---

## Output file convention

Scripts write raw LLM output to `Campaigns/_session_memory/YYYY-MM-DD_archivist.md` (or parse and append). If the LLM returns markdown with the above sections, preserve that structure; otherwise store raw and optionally parse later.
