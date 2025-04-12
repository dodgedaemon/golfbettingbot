from pathlib import Path
RAW_DIR = Path("data")

import requests
import pandas as pd

# DataGolf API URL for Bet365 Masters odds
url = "https://feeds.datagolf.com/betting-tools/outrights?tour=pga&event_id=14&market=win&book=bet365&odds_format=decimal&file_format=json&key=27ae4c1d702ce9a899bb4ff56cf9"

response = requests.get(url)
data = response.json()

# Extract only player name and bet365 odds
odds_data = []
for entry in data["odds"]:
    name = entry.get("player_name", "").strip()
    bet365_odds = entry.get("bet365", None)
    if name and bet365_odds is not None:
        # Normalize names to Firstname Lastname
        parts = name.split(",")
        player_name = parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name
        odds_data.append({"player_name": player_name, "bet365_odds": bet365_odds})

# Save to CSV
df = pd.DataFrame(odds_data)
df.to_csv(RAW_DIR / "bet365_odds.csv", index=False)

print(f"✅ Saved Bet365 odds for {len(df)} players.")
