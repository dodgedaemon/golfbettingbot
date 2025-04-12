from pathlib import Path
import requests
import pandas as pd

RAW_DIR = Path("data")
API_KEY = "27ae4c1d702ce9a899bb4ff56cf9"
url = f"https://feeds.datagolf.com/preds/skill-ratings?display=value&file_format=json&key={API_KEY}"

print("📡 Fetching detailed skill ratings from DataGolf...")

response = requests.get(url)

if response.status_code != 200:
    print(f"❌ Error: {response.status_code}", response.text)
    exit()

data = response.json()
players = data.get("players", [])
df = pd.DataFrame(players)

# Normalize names to Firstname Lastname
def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

df["player_name"] = df["player_name"].apply(normalize_name)

columns_to_keep = [
    "player_name", "sg_total", "sg_ott", "sg_app", "sg_arg", "sg_putt",
    "driving_dist", "driving_acc"
]

df = df[columns_to_keep]

df.to_csv(RAW_DIR / "skill_ratings.csv", index=False)
print(f"✅ Saved detailed stats for {len(df)} players to data/skill_ratings.csv")
