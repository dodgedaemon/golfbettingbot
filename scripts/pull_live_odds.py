import requests
import pandas as pd
from pathlib import Path

API_KEY = "97f1b0264c284b28f3288db8750b5236"
OUT_PATH = Path("data/live_betfair_odds.csv")

print("📡 Fetching live Betfair odds for the Masters...")

url = (
    "https://api.the-odds-api.com/v4/sports/golf_masters_tournament_winner/odds/"
    f"?regions=eu&markets=outrights&apiKey={API_KEY}"
)

response = requests.get(url)
if response.status_code != 200:
    print(f"❌ Failed to fetch odds: {response.status_code}")
    exit()

data = response.json()

# Search for Betfair bookmaker
betfair_data = None
for bookmaker in data[0].get("bookmakers", []):
    if bookmaker["key"] == "betfair_ex_eu":
        betfair_data = bookmaker
        break

if not betfair_data:
    print("❌ Betfair data not found.")
    exit()

# Extract outcomes
market = next((m for m in betfair_data["markets"] if m["key"] == "outrights"), None)
if not market:
    print("❌ Outright market not found.")
    exit()

outcomes = market["outcomes"]
odds_df = pd.DataFrame(outcomes)
odds_df.rename(columns={"name": "player_name", "price": "live_betfair_odds"}, inplace=True)

# Save
odds_df.to_csv(OUT_PATH, index=False)
print(f"✅ Saved live Betfair odds to {OUT_PATH} with {len(odds_df)} players.")
