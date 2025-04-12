import pandas as pd

# Load skill ratings
df = pd.read_csv("data/skill_ratings.csv")

# Normalize names
def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

df["player_name"] = df["player_name"].apply(normalize_name)

# Standardize the relevant stats
z_cols = ["sg_total", "sg_ott", "sg_app", "sg_arg", "sg_putt", "driving_dist", "driving_acc"]
for col in z_cols:
    df[col + "_z"] = (df[col] - df[col].mean()) / df[col].std()

# Compute augusta_fit_score (weight each stat if desired)
df["augusta_fit_score"] = (
    df["sg_ott_z"] * 0.25 +
    df["sg_app_z"] * 0.25 +
    df["driving_dist_z"] * 0.25 +
    df["driving_acc_z"] * 0.25
)

# Output file
df[["player_name", "augusta_fit_score"]].to_csv("data/augusta_fit_scores.csv", index=False)
print(f"✅ Created augusta_fit_scores.csv with {len(df)} players")
