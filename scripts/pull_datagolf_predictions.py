import requests
import pandas as pd
import json
from pathlib import Path

API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
RAW_DIR = Path("data")

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def pull_predictions(event: str, year: int):
    url = (
        "https://feeds.datagolf.com/preds/pre-tournament"
        "?tour=pga"
        "&add_position=17,23"
        "&dead_heat=yes"
        "&odds_format=decimal"
        "&file_format=json"
        f"&key={API_KEY}"
    )

    print(f"📡 Fetching pre-tournament predictions from DataGolf for {event} {year}...")
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        exit()

    try:
        raw_data = response.json()
    except json.JSONDecodeError:
        print("❌ Failed to parse JSON.")
        exit()

    for key, value in raw_data.items():
        if isinstance(value, list) and isinstance(value[0], dict) and "player_name" in value[0]:
            df = pd.DataFrame(value)
            break
    else:
        print("❌ Could not find a player array in the JSON.")
        exit()

    df["player_name"] = df["player_name"].apply(normalize_name)

    # Save event-specific file
    named_file = f"{event.lower()}_tournament_predictions_{str(year)[-2:]}.csv"
    df.to_csv(RAW_DIR / named_file, index=False)

    # Also save a generic version for live pipeline
    df.to_csv(RAW_DIR / "tournament_predictions.csv", index=False)

    print(f"✅ Saved predictions to:")
    print(f"   → data/{named_file}")
    print(f"   → data/tournament_predictions.csv (generic live file)")

if __name__ == "__main__":
    # 📁 Load event + year from meta file
    meta_path = RAW_DIR / "event_meta.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)
    event = meta["event"]
    year = meta["year"]

    pull_predictions(event, year)
