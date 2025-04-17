from pathlib import Path
import pandas as pd
import json

DATA_DIR = Path("data")

# Load event meta to dynamically pick the right file
with open(DATA_DIR / "event_meta.json", "r") as f:
    meta = json.load(f)
    event = meta["event"]
    year = meta["year"]

input_file = f"incomingform_eventhistory_{event}_{str(year)[-2:]}.csv"
df = pd.read_csv(DATA_DIR / input_file)

# Rename "Player" column to "player_name"
df = df.rename(columns={"Player": "player_name"})

# Identify year columns (e.g. 2024, 2023, ...)
year_cols = [col for col in df.columns if col != "player_name"]
recent_years = sorted(year_cols)[-3:]

# Scoring logic
def score_position(pos):
    pos = str(pos).strip().replace("^", "")
    if pos in {"-", "MC", "WD", "DQ"} or pos == "" or pd.isna(pos):
        return 0
    try:
        pos = int(pos)
        if pos == 1:
            return 10
        elif pos <= 5:
            return 4
        elif pos <= 10:
            return 3
        elif pos <= 25:
            return 2
        else:
            return 0.5
    except:
        return 0

def calc_score(row):
    total_score = 0
    event_count = 0

    for year in year_cols:
        score = score_position(row[year])
        if score > 0:
            weight = 1.25 if year in recent_years else 1.0
            total_score += score * weight
            event_count += 1

    if event_count == 0:
        return 0
    return round(total_score / event_count, 3)

# Apply scoring
df["course_history_score"] = df.apply(calc_score, axis=1)

# Output cleaned file
df_out = df[["player_name", "course_history_score"]]
df_out.to_csv(DATA_DIR / "course_history_scores_clean.csv", index=False)

print(f"✅ Saved course history scores for {len(df_out)} players.")
