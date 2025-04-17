import requests
import pandas as pd
from pathlib import Path
import json

API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
URL = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=win&odds_format=decimal&file_format=json&key={API_KEY}"
SAVE_PATH = Path("data/bet365_odds.csv")
EVENT_META_PATH = Path("data/event_meta.json")

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def main():
    print("📡 Fetching Bet365 odds from DataGolf...")
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"❌ Error {response.status_code}: {response.text}")
        return

    data = response.json()
    odds = data.get("odds", [])
    if not odds:
        print("⚠️ No odds found in response.")
        return

    df = pd.json_normalize(odds, sep="_")
    df["player_name"] = df["player_name"].apply(normalize_name)
    df = df[["player_name", "bet365", "datagolf_baseline", "datagolf_baseline_history_fit"]].copy()
    df = df.rename(columns={
        "datagolf_baseline": "baseline",
        "datagolf_baseline_history_fit": "baseline_history_fit"
    })

    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAVE_PATH, index=False)
    print(f"✅ Saved odds for {len(df)} players to {SAVE_PATH}")

    # Save event metadata
    event_name = data.get("event_name", "unknown").lower().replace(" ", "_")
    event_meta = {
        "event": event_name,
        "year": pd.to_datetime(data.get("last_updated")).year
    }

    EVENT_META_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENT_META_PATH, "w") as f:
        json.dump(event_meta, f, indent=2)
    print(f"📝 Saved event meta: {event_meta}")

if __name__ == "__main__":
    main()
