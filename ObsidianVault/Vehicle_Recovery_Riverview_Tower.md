# Vehicle Recovery — Riverview Tower Case

**Case:** Squad 165A, Control 26-049682 | **Precinct:** P1

---

## Status: Vehicle Recovered (2026-03)

**Vehicle recovered** — at owner's residence. Recovery location: **1515 Park Ave Minneapolis** (~5–9 min from scene).

---

## Post-Recovery: Stolen Item + Forensic Leads

### Stolen item (not recovered)

| Item | Details |
|------|---------|
| **NEO4IC ZYPHR 2 BLACK mantle jacket** | [Product page](https://neo4ic.com/products/zyphr-v2-mantle-black) — ~$180 retail |
| **Likely disposition** | Sold on used market (Mercari, Poshmark, FB Marketplace, Craigslist) |

### Forensic leads (in vehicle)

- **Chain smoking** — cigarette butts/packaging in trash
- **Wendy's** — no receipts found (2026-03-02)

---

## Stolen Vehicle (victim's)

| Field | Value |
|-------|-------|
| Make/Model | 2008 Hyundai Santa Fe, Blue Black |
| VIN | 5NMSH73R18H204397 |
| Plate | ZHL 655 |

---

## Perp Vehicle

| Field | Value |
|-------|-------|
| Vehicle | Ford Taurus |
| Plate | Dealer paper plate, no front plate [fill if known] |
| Time window | 9:16–9:36 PM |
| Suspects | Two Caucasian men; one average build/height; one heavier set, unhealthy |

---

## Crime Scene

- **Address:** 1920 S 1st St APT 1503, Minneapolis MN 55454 (Riverview Tower)
- **Coordinates:** 44.962, -93.242

---

## Camera Map Summary

- **OSM ALPRs:** MPD Insight LPR (44.97, -93.25), UMN Flock (44.97, -93.24) — both north of scene
- **511mn.org:** I-35W @ Hiawatha, multiple I-35W cameras. Enable cameras layer; zoom Minneapolis.
- **Traffic Cam Archive:** No Minnesota coverage currently.
- **Full map:** `.cursor/state/adhoc/vehicle_recovery_cameras_20260228.md`
- **FOIA checklist:** `.cursor/state/adhoc/vehicle_recovery_foia_checklist.md`

---

## StolenCar.com — Register Process

**Note (2026-02):** Site unreachable (verified 2026-02-29: chrome-error for http and https). Alternative: manual police report registration.

1. Call 911 to report (if not done).
2. Go to https://www.stolencar.com/Register (verify site is reachable).
3. Register vehicle in StolenCar.com database (publicly accessible).
4. Activates neighborhood watch; members get email/push alerts.
5. Members who spot the vehicle call police and report to StolenCar.com; rewards on recovery.

**Join as member (free):** https://www.stolencar.com/User/Signup — receive alerts for stolen vehicles in your area.

---

## NICB VINCheck — Monitor Process

**Automated (optional):** Run `python local-proto/scripts/vehicle_recovery_nicb_check.py` daily. Logs to `vehicle_recovery_nicb_log.md`. Max 5/day. Use `--manual` to log a manual run. **Scheduled:** See SCHEDULE_VEHICLE_RECOVERY.md.

**Manual:**
1. Go to https://www.nicb.org/vincheck
2. Enter VIN: 5NMSH73R18H204397
3. Accept terms; search.
4. **Limit:** 5 searches per 24 hours per IP.
5. **Note:** VINCheck queries insurance theft/salvage records only, not law enforcement. Useful to monitor if vehicle resurfaces in insurance system.

---

## Marketplace Monitoring

### Vehicle (obsolete — vehicle recovered)

**Automated (optional):** Run `python local-proto/scripts/vehicle_recovery_marketplace_scrape.py` to search Craigslist for "2008 Santa Fe", "Santa Fe blue". Output: `vehicle_recovery_marketplace_*.json`; diff shows new listings.

**Scheduled runs:** See [SCHEDULE_VEHICLE_RECOVERY.md](D:\CodeRepositories\local-proto\docs\SCHEDULE_VEHICLE_RECOVERY.md). Use `run_vehicle_recovery_scheduled.ps1` for both NICB + marketplace; Task Scheduler setup included.

### Stolen jacket (NEO4IC ZYPHR 2 BLACK)

**Manual search** — check used market for jacket (~$180 retail; likely resold):

| Platform | Search keywords |
|----------|-----------------|
| Craigslist Minneapolis | `NEO4IC`, `ZYPHR`, `Zyphr mantle`, `techwear black jacket` |
| Facebook Marketplace | `NEO4IC ZYPHR`, `Zyphr 2`, `techwear mantle` |
| Poshmark | `NEO4IC`, `Zyphr mantle black` |
| Mercari | `NEO4IC`, `Zyphr`, `techwear jacket` |
| Depop | `NEO4IC`, `Zyphr`, `cyberpunk jacket` |

**Geography:** Minneapolis / Twin Cities / Minnesota — suspects left vehicle at 1515 Park Ave; may sell locally.

**Last searched:** 2026-03-02 — see [vehicle_recovery_jacket_marketplace_20260302.md](D:\CodeRepositories\.cursor\state\adhoc\vehicle_recovery_jacket_marketplace_20260302.md). No ZYPHR 2 mantle on Craigslist; Mercari has NEO4IC items (manual review); Poshmark NEO4IC items not mantle; FB Marketplace requires login.

---

## Platform Expansion (post to all)

- **Ring Neighbors** — radius around 1920 S 1st St
- **Nextdoor** — Riverview Tower area, Seward, Longfellow, Prospect Park
- **FB groups** — "Minneapolis Stolen Cars", neighborhood groups
- **Reddit** — r/Minneapolis
- **Buy Nothing** — Seward, Longfellow, Prospect Park, Marcy-Holmes

## Geography Expansion (neighborhoods along escape routes)

S 1st St, Franklin Ave, Hiawatha Ave, I-35W, Cedar Ave, Seward, Longfellow, Prospect Park, Marcy-Holmes.

---

## Community Post Template v2 (Ring / Nextdoor / FB / Reddit / Buy Nothing)

```
STOLEN: 2008 Hyundai Santa Fe, Blue Black
Location: 1920 S 1st St (Riverview Tower), Minneapolis
Time: 9:16–9:36 PM [date]
VIN: 5NMSH73R18H204397
Plate: ZHL 655

Perp vehicle: Ford Taurus, dealer paper plate, no front plate.
Two suspects: one average build, one heavier set.

If you have doorbell or security footage from 8:30–10:30 PM near Riverview Tower, S 1st St, Franklin, Hiawatha, I-35W, Cedar Ave, Seward, Longfellow, or Prospect Park, please contact Minneapolis Police Squad 165A, Case 26-049682.
```

---

## GhostTrack / Maigret Trigger

Use **only** when suspect username or phone emerges from community (Nextdoor, Ring, social). Require human approval before lookup. Per TOOL_SAFEGUARDS: output `APPROVAL_NEEDED` and wait.

---

## Update Process (when new cameras or leads found)

1. Append to camera map: `.cursor/state/adhoc/vehicle_recovery_cameras_*.md`
2. Update detective one-pager: `.cursor/state/adhoc/vehicle_recovery_detective_onepager.md`
3. Notify detective (human action)
4. NICB and marketplace scripts do not auto-notify; review logs and decide when to update detective
