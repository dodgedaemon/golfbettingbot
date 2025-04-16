import requests
import pandas as pd
import json
from pathlib import Path
import argparse

API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
RAW_DIR = Path("data")

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def pull_live_predictions(event: str, year: int):
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

    df = pd.DataFrame(players)
    df["player_name"] = df["player_name"].apply(normalize_name)

    # Save both versions
    named_file = f"live_predictions_{event.lower()}_{str(year)[-2:]}.csv"
    df.to_csv(RAW_DIR / named_file, index=False)
    df.to_csv(RAW_DIR / "live_predictions.csv", index=False)

    print(f"✅ Saved live in-play predictions for {len(df)} players:")
    print(f"   → data/{named_file}")
    print(f"   → data/live_predictions.csv (generic live file)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="Event name, e.g. rbc")
    parser.add_argument("--year", required=True, type=int, help="Year, e.g. 2025")
    args = parser.parse_args()

    pull_live_predictions(args.event, args.year)
