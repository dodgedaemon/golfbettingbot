from pathlib import Path
import argparse
import requests
import pandas as pd

DATA_DIR = Path("data")
API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def pull_dg_rankings(event: str, year: int):
    url = f"https://feeds.datagolf.com/preds/get-dg-rankings?file_format=json&key={API_KEY}"
    print("📡 Fetching DataGolf rankings and tour info...")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}", response.text)
        exit()

    data = response.json()
    players = data.get("rankings", [])
    df = pd.DataFrame(players)
    df["player_name"] = df["player_name"].apply(normalize_name)

    # Save both files
    named_file = f"datagolf_rankings_{event.lower()}_{str(year)[-2:]}.csv"
    df.to_csv(DATA_DIR / named_file, index=False)
    df.to_csv(DATA_DIR / "datagolf_rankings.csv", index=False)

    print(f"✅ Saved DataGolf rankings for {len(df)} players:")
    print(f"   → data/{named_file}")
    print(f"   → data/datagolf_rankings.csv (generic live file)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="Event name, e.g. rbc")
    parser.add_argument("--year", required=True, type=int, help="Year, e.g. 2025")
    args = parser.parse_args()

    pull_dg_rankings(args.event, args.year)
