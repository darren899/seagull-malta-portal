#!/usr/bin/env python3
"""
Seagull Maritime - Malta Portal Personnel Refresh
==================================================

Run this every ~2 weeks after exporting the latest personnel CSV from 1Clearview.

WHAT IT DOES
------------
Reads a raw CSV export from 1Clearview (all PCASP fields) and produces the
anonymised roster JSON that the Malta portal reads at page load.

WHAT IT KEEPS (Licensing-Board-appropriate)
-------------------------------------------
  - ref            - sequential portal reference (PCASP-001 ... PCASP-NNN)
  - nationality    - normalised (Sri Lankan / Indian / Ukrainian / Nepalese ...)
  - capability     - normalised role class:
                       * Team Leader Capable   (TL/TM/2IC/CMS/All)
                       * Team Member           (TM/2IC/CMS)
                       * RALL Specialist       (TM/2IC/CMS/RALL)
  - vaccinated     - true/false
  - status         - BOOKED / IN TRANSIT

WHAT IT DROPS (personal / operationally sensitive)
--------------------------------------------------
  Names, DOB, passport numbers + expiry, addresses, phone, email,
  specific vessel assignments, airport codes, DNU reasons.

USAGE
-----
  python refresh-personnel.py path/to/personnel.csv

Then commit the updated personnel-roster.json via GitHub Desktop.
"""

import csv
import json
import sys
from pathlib import Path
from datetime import date


def normalise_nationality(raw: str) -> str:
    if not raw:
        return "Unknown"
    v = raw.strip().lower()
    if "sri" in v:
        return "Sri Lankan"
    if v == "indian" or "india" in v:
        return "Indian"
    if "ukrain" in v:
        return "Ukrainian"
    if "nepal" in v:
        return "Nepalese"
    return raw.strip().title()


def normalise_capability(roles: str) -> str:
    if not roles:
        return "Team Member"
    r = roles.upper()
    if "RALL" in r:
        return "RALL Specialist"
    if "ALL" in r:
        return "Team Leader Capable"
    return "Team Member"


def normalise_vaccinated(raw: str) -> bool:
    if not raw:
        return False
    return "vaccin" in raw.strip().lower()


def find_status_from_row(row: dict) -> str:
    """
    1Clearview CSV export has header/data column-count drift
    ("Theatre Days" header shipped but no data), so scan every value
    and pick up BOOKED / IN TRANSIT wherever they actually land.
    """
    for v in row.values():
        if v is None:
            continue
        u = str(v).strip().upper()
        if u == "BOOKED":
            return "BOOKED"
        if u == "IN TRANSIT":
            return "IN TRANSIT"
    return "Unknown"


def process(csv_path: Path, out_path: Path) -> None:
    roster = []
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            roster.append({
                "ref": f"PCASP-{i:03d}",
                "nationality": normalise_nationality(row.get("Nationality", "")),
                "capability": normalise_capability(row.get("Roles", "")),
                "vaccinated": normalise_vaccinated(row.get("Credentials", "")),
                "status": find_status_from_row(row),
            })

    by_nationality, by_capability, by_status = {}, {}, {}
    vaccinated_count = 0
    for p in roster:
        by_nationality[p["nationality"]] = by_nationality.get(p["nationality"], 0) + 1
        by_capability[p["capability"]] = by_capability.get(p["capability"], 0) + 1
        by_status[p["status"]] = by_status.get(p["status"], 0) + 1
        if p["vaccinated"]:
            vaccinated_count += 1

    payload = {
        "last_updated": date.today().isoformat(),
        "source_system": "1Clearview ERP (internal)",
        "total_records": len(roster),
        "summary": {
            "by_nationality": dict(sorted(by_nationality.items(), key=lambda x: -x[1])),
            "by_capability": dict(sorted(by_capability.items(), key=lambda x: -x[1])),
            "by_status": dict(sorted(by_status.items(), key=lambda x: -x[1])),
            "vaccinated": vaccinated_count,
            "vaccinated_pct": round(100 * vaccinated_count / len(roster), 1) if roster else 0,
        },
        "roster": roster,
        "notes": {
            "data_minimisation": (
                "Published fields are limited to those appropriate for Licensing Board "
                "oversight of PCASP capability. Personal data (names, DOB, passport, "
                "address, phone, email) and operationally sensitive data (vessel "
                "assignments) are held internally on 1Clearview ERP and SM/INT/REG/008 "
                "and available to the Board on request under confidentiality."
            ),
            "refresh_cadence": "Refreshed approximately every two weeks.",
        },
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}  ({len(roster)} records)")
    print(f"  Nationalities: {payload['summary']['by_nationality']}")
    print(f"  Capabilities:  {payload['summary']['by_capability']}")
    print(f"  Status:        {payload['summary']['by_status']}")
    print(f"  Vaccinated:    {vaccinated_count}/{len(roster)} ({payload['summary']['vaccinated_pct']}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python refresh-personnel.py <path-to-personnel.csv>")
        sys.exit(1)
    csv_path = Path(sys.argv[1]).resolve()
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}")
        sys.exit(1)
    out_path = Path(__file__).resolve().parent / "personnel-roster.json"
    process(csv_path, out_path)
