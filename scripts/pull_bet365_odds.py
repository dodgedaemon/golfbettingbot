import argparse
import requests
import pandas as pd
from pathlib import Path

API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
RAW_DIR = Path("data")

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def pull_bet365_odds(event: str, year: int):
    # 🔥 Hardcoded for now (optional: use event_id mapping file)
    # event_id=14 is for the Masters; can be dynamic later
    url = (
        "https://feeds.datagolf.com/betting-tools/outrights"
        f"?tour=pga&market=win&book=bet365&odds_format=decimal"
        f"&file_format=json&key={API_KEY}"
    )

    print("📡 Fetching Bet365 odds from DataGolf...")
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Error:", response.status_code, response.text)
        exit()

    data = response.json()
    odds_data = []
    for entry in data.get("odds", []):
        name = entry.get("player_name", "").strip()
        bet365_odds = entry.get("bet365", None)
        if name and bet365_odds is not None:
            odds_data.append({
                "player_name": normalize_name(name),
                "bet365_odds": bet365_odds
            })

    df = pd.DataFrame(odds_data)

    # Save both files
    out_file = f"bet365_odds_{event.lower()}_{str(year)[-2:]}.csv"
    df.to_csv(RAW_DIR / out_file, index=False)
    df.to_csv(RAW_DIR / "bet365_odds.csv", index=False)

    print(f"✅ Saved Bet365 odds for {len(df)} players:")
    print(f"   → data/{out_file}")
    print(f"   → data/bet365_odds.csv (generic live file)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="Event name, e.g. rbc")
    parser.add_argument("--year", required=True, type=int, help="Year, e.g. 2025")
    args = parser.parse_args()

    pull_bet365_odds(args.event, args.year)
