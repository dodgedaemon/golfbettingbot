import pandas as pd

files = [
    "data/sg_wells_fargo_24.csv",
    "data/sg_east_lake_24.csv",
    "data/sg_arnold_palmer_25.csv",
    "data/sg_genesis_25.csv"
]

# Load CSVs with semicolon delimiter
dfs = []
for f in files:
    df = pd.read_csv(f, delimiter=";")
    df["source"] = f
    dfs.append(df)

# Combine all event data
combined = pd.concat(dfs, ignore_index=True)

# Normalize player names
def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

combined["player_name"] = combined["Player"].apply(normalize_name)

# SG stats columns
sg_cols = ["SG-OTT", "SG-APP", "SG-ATG", "SG-P", "SG-TOT"]

# Fix '#FIELD!x' values and convert to numeric
for col in sg_cols:
    combined[col] = (
        combined[col]
        .astype(str)
        .str.replace("#FIELD!", "-", regex=False)
        .replace("-", "-0.0")  # in case it's just "-"
    )
    combined[col] = pd.to_numeric(combined[col], errors="coerce")

# Drop rows with no valid SG data
combined.dropna(subset=sg_cols, how="all", inplace=True)

# Aggregate average SG per player
agg_df = combined.groupby("player_name")[sg_cols].mean().reset_index()

# Weighted composite score
agg_df["sg_composite_fit_score"] = (
    0.3 * agg_df["SG-OTT"] +
    0.3 * agg_df["SG-APP"] +
    0.1 * agg_df["SG-ATG"] +
    0.1 * agg_df["SG-P"] +
    0.2 * agg_df["SG-TOT"]
)

# Save output
agg_df.to_csv("data/sg_composite_fit_scores.csv", index=False)
print("✅ sg_composite_fit_scores.csv created with cleaned values.")
