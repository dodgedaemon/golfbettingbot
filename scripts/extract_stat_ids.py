import json
import csv
from pathlib import Path

# Paths
INPUT_PATH = Path("data/pgatour_response.json")
OUTPUT_PATH = Path("data/stat_id_mapping_full.csv")

# Load JSON
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Navigate into nested structure
categories = data.get("data", {}).get("statDetails", {}).get("statCategories", [])

# Flatten into list of rows
rows = []
for cat in categories:
    cat_name = cat.get("displayName", "")
    for sub in cat.get("subCategories", []):
        sub_name = sub.get("displayName", "")
        for stat in sub.get("stats", []):
            stat_id = stat.get("statId")
            stat_title = stat.get("statTitle")
            if stat_id and stat_title:
                rows.append({
                    "category": cat_name,
                    "subcategory": sub_name,
                    "stat_id": stat_id,
                    "stat_title": stat_title
                })

# Save to CSV
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["category", "subcategory", "stat_id", "stat_title"])
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Extracted {len(rows)} stat IDs to {OUTPUT_PATH}")
