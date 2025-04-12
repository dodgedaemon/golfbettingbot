from pathlib import Path
import requests
import pandas as pd

DATA_DIR = Path("data")

# DataGolf API Key
API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"

# Endpoint
url = f"https://feeds.datagolf.com/preds/get-dg-rankings?file_format=json&key={API_KEY}"

print("📡 Fetching DataGolf rankings and tour info...")

# Send request
response = requests.get(url)

# Error handling
if response.status_code != 200:
    print(f"❌ Error: {response.status_code}", response.text)
    exit()

# Parse JSON response
data = response.json()

# Extract players
players = data.get("rankings", [])
df = pd.DataFrame(players)

# Clean up player names
df["player_name"] = df["player_name"].str.strip()

# Save to disk
output_file = DATA_DIR / "datagolf_rankings.csv"
df.to_csv(output_file, index=False)
print(f"✅ Saved DataGolf rankings for {len(df)} players to {output_file}")
