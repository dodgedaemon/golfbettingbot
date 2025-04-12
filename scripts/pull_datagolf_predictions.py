import requests
import pandas as pd
import json
from pathlib import Path

API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
RAW_DIR = Path("data")

url = (
    "https://feeds.datagolf.com/preds/pre-tournament"
    "?tour=pga"
    "&add_position=17,23"
    "&dead_heat=yes"
    "&odds_format=decimal"
    "&file_format=json"
    f"&key={API_KEY}"
)

print("📡 Fetching pre-tournament predictions from DataGolf...")

response = requests.get(url)
if response.status_code != 200:
    print("❌ Error:", response.status_code, response.text)
    exit()

try:
    raw_data = response.json()
except json.JSONDecodeError:
    print("❌ Failed to parse JSON.")
    exit()

# Extract player array
for key, value in raw_data.items():
    if isinstance(value, list) and isinstance(value[0], dict) and "player_name" in value[0]:
        df = pd.DataFrame(value)
        event_name = raw_data.get("event_name", "masters2025")
        break
else:
    print("❌ Could not find a player array in the JSON.")
    exit()

# Normalize player names to Firstname Lastname
def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

df["player_name"] = df["player_name"].apply(normalize_name)

# Save
df.to_csv(RAW_DIR / "masters_tournament_predictions.csv", index=False)
print(f"✅ Saved predictions to data/masters_tournament_predictions.csv with {len(df)} players.")
