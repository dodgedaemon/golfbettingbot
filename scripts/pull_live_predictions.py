import requests
import pandas as pd
import json
from pathlib import Path

API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
RAW_DIR = Path("data")

url = (
    "https://feeds.datagolf.com/preds/in-play"
    "?tour=pga"
    "&dead_heat=no"
    "&odds_format=percent"
    "&file_format=json"
    f"&key={API_KEY}"
)

print("📡 Fetching live in-play predictions from DataGolf...")

response = requests.get(url)
if response.status_code != 200:
    print("❌ Error:", response.status_code, response.text)
    exit()

try:
    raw_data = response.json()
    players = raw_data.get("data", [])
except json.JSONDecodeError:
    print("❌ Failed to parse JSON.")
    exit()

if not players or "player_name" not in players[0]:
    print("❌ Could not find valid player data in JSON.")
    exit()

# Normalize player names to Firstname Lastname
def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

df = pd.DataFrame(players)
df["player_name"] = df["player_name"].apply(normalize_name)

# Save
df.to_csv(RAW_DIR / "live_predictions.csv", index=False)
print(f"✅ Saved live in-play predictions to data/live_predictions.csv with {len(df)} players.")
