# Personnel Roster Refresh — Operating Note

**Owner:** Group Compliance Director (Darren Watts)
**Cadence:** ~Every 2 weeks (aligned with 1Clearview deployment cycle)
**Output:** `personnel-roster.json` (published to the Malta portal, Personnel section)

---

## What this does

The Malta Licensing Board wants evidence that our PCASP pool is real, at scale, vetted, and current. This folder holds a small Python script that takes a raw personnel CSV exported from 1Clearview ERP and produces an **anonymised roster JSON** that the Malta portal loads at page open.

The portal page (`/personnel/`) fetches that JSON, renders the stats (total / deployed / booked / vaccination %), the nationality / capability / status breakdowns, the filter pills and the scrollable roster table. If the JSON is missing or unreadable, the page shows a fallback message and never breaks.

**We publish anonymised. Named data stays internal.** The Board can request the named roster under confidentiality at any time — the portal says so in the footer of that section.

---

## What the script keeps vs drops

**Published to the portal (Licensing-Board-appropriate):**

- `ref` — sequential portal reference (`PCASP-001` ... `PCASP-NNN`)
- `nationality` — normalised (Sri Lankan / Indian / Ukrainian / Nepalese / ...)
- `capability` — normalised role class:
  - **Team Leader Capable** — TL / TM / 2IC / CMS / All
  - **Team Member** — TM / 2IC / CMS
  - **RALL Specialist** — TM / 2IC / CMS / RALL
- `vaccinated` — true / false
- `status` — BOOKED / IN TRANSIT

**Held internally (NOT in the published JSON):**

Names, DOB, passport number and expiry, home address, phone, email, specific vessel assignments, airport codes, DNU reasons. All of that lives on 1Clearview ERP and in the internal `SM/INT/REG/008` training and competence matrix — available to the Board on request under confidentiality.

This is the data-minimisation answer we give the Board if they ask why we don't publish names on the gated portal. Short version: gated ≠ licensed, and the Schedule doesn't ask for named personal data on the portal.

---

## Running the refresh (step by step)

**1. Export the live CSV from 1Clearview**

Standard all-PCASP export. Whatever the default filename is — doesn't matter, we point the script at it.

Common 1Clearview export quirk: the header row ships 22 columns but data rows only ship 21 values (the "Theatre Days" column header has no data). The script handles this — do not "fix" the CSV by hand.

**2. Drop the CSV somewhere you can find it**

Anywhere is fine. Downloads folder, Desktop, this folder — it doesn't matter. The script takes a path.

**3. Run the refresh**

Open a terminal / PowerShell, cd into this folder, and run:

```
python refresh-personnel.py "C:\path\to\personnel.csv"
```

The script will print a summary to the terminal — total records, nationality breakdown, capability breakdown, status breakdown, vaccination %.

Sanity check against what you'd expect. Last run (22 Apr 2026) baseline:

- Total: 175
- Nationality: Sri Lankan 98 · Indian 62 · Ukrainian 12 · Nepalese 3
- Capability: Team Member 75 · Team Leader Capable 65 · RALL Specialist 35
- Status: IN TRANSIT 130 · BOOKED 45
- Vaccinated: 172 / 175 (98.3%)

If a number looks off by orders of magnitude, stop and check the CSV export — a column drift in 1Clearview will usually show up as Status = "Unknown" for most rows.

**4. Commit via GitHub Desktop**

The script writes `personnel-roster.json` alongside itself. GitHub Desktop will pick up the change to that one file. Commit message like:

```
Personnel roster refresh — 22 Apr 2026 (175 records)
```

Push. Done. The portal will serve the new JSON on the next page load (no CDN cache — the fetch is `cache: 'no-cache'`).

**5. Spot-check the live portal**

Open `malta.seagullmaritimeltd.com/personnel/` and confirm the "Last refreshed" stamp shows today's date and the numbers match what the terminal printed.

---

## Troubleshooting

**Status column shows "Unknown" for most rows**

The 1Clearview CSV header row and data row column counts drift. The script scans every value in each row for `BOOKED` or `IN TRANSIT` so it doesn't care which column those land in — but if the CSV is mangled in some new way (extra empty columns, truncated rows), the heuristic will fail. Open the CSV in Excel and eyeball it against a known-good export.

**Nationality shows as "India" instead of "Indian" (or similar)**

The normaliser handles "sri", "india", "ukrain", "nepal" as case-insensitive substring matches. Anything else falls through to title-case of the raw value. If a new nationality shows up, add it to `normalise_nationality()` in the script.

**The page is stuck on "Loading roster…"**

The JSON fetch failed. Most likely: the JSON file didn't get pushed to GitHub, or the filename got renamed. Confirm `personnel-roster.json` is in `/personnel/data/` on the `main` branch of `seagull-malta-portal-repo`.

**You changed the script and now it errors**

Known OneDrive gotcha: the Write/Edit tools Claude uses can truncate large files on OneDrive paths. If Claude edited this script and it now fails mid-run, it may have been truncated. Scroll to the bottom — the last line should be `process(csv_path, out_path)`. If the file just stops mid-function, get Claude to rewrite it via bash heredoc rather than Edit.

---

## Who sees what

| Surface | What it shows | Who it's for |
|---|---|---|
| Malta portal `/personnel/` | Anonymised roster (ref / nationality / capability / vax / status) | Transport Malta Licensing Board (gated `MALTA-SEA-2026`) |
| `SM/INT/REG/008` Training & Competence Matrix | Full named roster + qualifications + dates | Internal — available to Board on request under confidentiality |
| 1Clearview ERP | Everything (names, passports, addresses, vessel assignments) | Operations team, GCD |

---

## Refresh cadence

Target every 2 weeks. Not critical if it slips — the portal's "Last refreshed" stamp is honest about when the data was last pulled, and a stale roster with a stale stamp is a hundred times better than a fresh-looking dashboard that quietly points at a month-old JSON.

Scheduled task **not** set up for this — it requires pulling the CSV out of 1Clearview manually, and that's a human-in-the-loop moment where we want Darren eyeballing the data before it goes live. Keep it that way.

---

*This folder and script are version-controlled with the rest of the portal. If the pattern changes (new fields, new normalisation rules, new categories), update `refresh-personnel.py` and this README together, and note the change in the Malta portal `live.html` timeline.*
