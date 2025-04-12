from pathlib import Path
import pandas as pd

# Updated path
DATA_DIR = Path("data")

# Load the raw course history CSV
df = pd.read_csv(DATA_DIR / "course_history_scores.csv")

# Identify the year columns
core_cols = ['player_name', 'Events', 'Av Score']
year_cols = [col for col in df.columns if col not in core_cols]

# Use last 3 years for recency weighting
recent_years = sorted(year_cols)[-3:]

# Scoring rules
def score_position(pos):
    try:
        if pos == '-' or pd.isna(pos):
            return 0
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

# Calculate weighted course history score
def calc_score(row):
    total = 0
    for year in year_cols:
        score = score_position(row[year])
        weight = 1.25 if year in recent_years else 1.0
        total += score * weight
    try:
        events = int(row['Events'])
        if events == 0:
            events = 1
    except:
        events = 1
    return round(total / events, 3)

df["course_history_score"] = df.apply(calc_score, axis=1)

# Output
df_out = df[["player_name", "course_history_score"]]
df_out.to_csv(DATA_DIR / "course_history_scores_clean.csv", index=False)

print(f"✅ Saved course history scores for {len(df_out)} players.")
