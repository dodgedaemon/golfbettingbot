# scripts/extract_event_ids.py

import json
import csv
from pathlib import Path

INPUT_FILE = Path("data/pgatour_response.json")
OUTPUT_FILE = Path("data/event_id_mapping.csv")
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

tournaments = data.get("data", {}).get("statDetails", {}).get("tournamentPills", [])
rows = []

for item in tournaments:
    original_event_id = item.get("tournamentId")
    event_name = item.get("displayName")

    if not original_event_id or not event_name:
        continue

    # Extract components
    tour = original_event_id[0]         # 'R'
    year = int(original_event_id[1:5])  # 2024
    pgaid = original_event_id[5:]       # '014'

    for new_year in YEARS:
        new_event_id = f"{tour}{new_year}{pgaid}"
        rows.append({
            "event_id": new_event_id,
            "event_name": event_name,
            "tour": tour,
            "year": new_year,
            "pgaid": pgaid
        })

# Write to CSV
with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["event_id", "event_name", "tour", "year", "pgaid"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Extracted {len(rows)} events to {OUTPUT_FILE}")
