from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")

# Load recent form and tour data
form_df = pd.read_csv(DATA_DIR / "incoming_form.csv")
tour_df = pd.read_csv(DATA_DIR / "datagolf_rankings.csv")

# Normalize names
form_df["player_name"] = form_df["player_name"].str.strip()
tour_df["player_name"] = tour_df["player_name"].str.strip()

# Map player -> primary tour
tour_map = tour_df.set_index("player_name")["primary_tour"].to_dict()

# Columns to evaluate
recent_cols = ["1", "2", "3", "4", "5", "6"]

# Tour multipliers
tour_multipliers = {
    "PGA": 1.0,
    "EURO": 1.15,
    "DPWT": 1.15,
    "LIV": 1.25,
    "KFT": 0.95,
    "CHAMP": 0.9,
    "ASA": 0.9,
    "JPN": 0.95,
    "PTA": 0.9,
    "AM": 0.85,
    "KOR": 0.9,
    "AFR": 0.9,
    "CHA": 0.9,
    "TPT": 0.9,
    "ANZ": 0.9
}

# Parse result values
def parse_result(val):
    val = str(val).replace("^", "").strip()
    if val.upper() == "MC":
        return 50.0
    try:
        return float(val)
    except:
        return None

# Compute recent form score
def calculate_score(row):
    name = row["player_name"]
    tour = tour_map.get(name, "PGA")
    multiplier = tour_multipliers.get(tour, 1.0)

    total, weight, wins = 0.0, 0, 0
    for i, col in enumerate(recent_cols):
        result = parse_result(row.get(col, None))
        if result is not None:
            total += result * multiplier
            weight += 1
            if i < 3 and result == 1.0:
                wins += 1

    if weight == 0:
        return 75.0

    avg = total / weight
    avg -= wins * 3
    return round(avg, 2)

# Apply
form_df["recent_form_score"] = form_df.apply(calculate_score, axis=1)

# Output to flat data directory
out_df = form_df[["player_name", "recent_form_score"]]
out_df.to_csv(DATA_DIR / "recent_form_scores.csv", index=False)

print(f"✅ Saved recent form scores for {len(out_df)} players to data/recent_form_scores.csv")
