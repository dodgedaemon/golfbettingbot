import pandas as pd
import json
import sys
from pathlib import Path

# Add utils path for dynamic weights loader
sys.path.append(str(Path(__file__).resolve().parent))
from utils.load_weights import load_weights

# Load weights
weights = load_weights()

# Load input data
preds_df = pd.read_csv("data/tournament_predictions.csv")
fit_df = pd.read_csv("data/sg_composite_fit_scores.csv")  # Includes event_fit_score and SG components
history_df = pd.read_csv("data/course_history_scores_clean.csv")
bet365_df = pd.read_csv("data/bet365_odds.csv").rename(columns={"bet365": "bet365_odds"})
skills_df = pd.read_csv("data/skill_ratings.csv")
live_df = pd.read_csv("data/live_predictions.csv")
live_odds_df = pd.read_csv("data/live_betfair_odds.csv")
dg_ranks_df = pd.read_csv("data/datagolf_rankings.csv")

# Merge all data
merged = preds_df.merge(fit_df, on="player_name", how="left")
merged = merged.merge(history_df, on="player_name", how="left")
merged = merged.merge(bet365_df, on="player_name", how="left")
merged = merged.merge(skills_df[["player_name", "driving_dist", "driving_acc"]], on="player_name", how="left")
merged = merged.merge(dg_ranks_df[["dg_id", "datagolf_rank"]], on="dg_id", how="left")

# Fill and convert
merged["event_fit_score"] = pd.to_numeric(merged.get("event_fit_score", 0), errors="coerce").fillna(0)
merged["course_history_score"] = pd.to_numeric(merged["course_history_score"], errors="coerce").fillna(0)
merged["driving_dist"] = pd.to_numeric(merged["driving_dist"], errors="coerce").fillna(0)
merged["driving_acc"] = pd.to_numeric(merged["driving_acc"], errors="coerce").fillna(0)
merged["win"] = pd.to_numeric(merged["win"], errors="coerce")
merged["bet365_odds"] = pd.to_numeric(merged["bet365_odds"], errors="coerce")

# Calculate SG Current Form Score using event_fit_components weights
sg_components = ["sg_ott", "sg_app", "sg_atg", "sg_putt", "sg_t2g", "sg_bst", "driving_dist", "driving_acc"]

def calculate_sg_current_form(row):
    total = 0
    for comp in sg_components:
        if comp in row:
            weight = weights["event_fit_components"].get(comp, 0)
            total += row[comp] * weight
    return total

merged["sg_current_form_score"] = merged.apply(calculate_sg_current_form, axis=1)

# Calculate the model score based on weighted averages
merged["your_model_score"] = (
    merged["event_fit_score"] * weights["event_fit_score_weight"] +
    merged["sg_current_form_score"] * weights["sg_current_form_score_weight"] +
    merged["course_history_score"] * weights["course_history_score_weight"] +
    merged["driving_dist"] * weights["event_fit_components"]["driving_dist"] +
    merged["driving_acc"] * weights["event_fit_components"]["driving_acc"]
)

# Final model score
merged["final_score"] = merged["your_model_score"]

# Value calculations
merged["dg_implied_prob"] = 1 / merged["win"]
merged["bet365_implied_prob"] = 1 / merged["bet365_odds"]

merged["your_implied_prob"] = (
    weights["datagolf_win_weight"] * merged["dg_implied_prob"] +
    weights["your_model_weight"] * (merged["final_score"] / merged["final_score"].sum())
)

merged["your_fair_odds"] = 1 / merged["your_implied_prob"]
merged["value_delta"] = merged["your_implied_prob"] - merged["bet365_implied_prob"]
merged["expected_value"] = merged["your_implied_prob"] * (merged["bet365_odds"] * 10) - 10
merged["roi_percent"] = (merged["expected_value"] / 10) * 100

# Save outputs (including SG breakdowns for later inspection)
merged.to_csv("data/ranked_predictions_with_form.csv", index=False)
merged.head(10).to_csv("data/top_10_predictions_with_form.csv", index=False)
merged.sort_values("expected_value", ascending=False).to_csv("data/top_value_bets.csv", index=False)
merged.query("event_fit_score > 0 & course_history_score > 0") \
    .sort_values("expected_value", ascending=False) \
    .to_csv("data/top_value_bets_with_model_input.csv", index=False)

# Live predictions merge
live_df["win"] = pd.to_numeric(live_df["win"], errors="coerce")
live_merged = merged.merge(live_df[["dg_id", "win"]], on="dg_id", how="left", suffixes=("", "_live"))

# Merge live odds
live_odds_df["live_betfair_odds"] = pd.to_numeric(live_odds_df["live_betfair_odds"], errors="coerce")
live_merged = live_merged.merge(live_odds_df, on="player_name", how="left")

# Add round info
live_merged = live_merged.merge(
    live_df[["dg_id", "current_score", "current_pos", "round", "thru", "today"]],
    on="dg_id", how="left"
)

# Live value calcs
live_merged["live_dg_implied_prob"] = live_merged["win_live"]
live_merged["live_your_implied_prob"] = (
    weights["live_datagolf_win_weight"] * live_merged["live_dg_implied_prob"] +
    weights["live_your_model_weight"] * (live_merged["final_score"] / live_merged["final_score"].sum())
)

live_merged["live_your_fair_odds"] = 1 / live_merged["live_your_implied_prob"]
live_merged["live_value_delta"] = live_merged["live_your_implied_prob"] - (1 / live_merged["live_betfair_odds"])
live_merged["live_expected_value"] = live_merged["live_your_implied_prob"] * (live_merged["live_betfair_odds"] * 10) - 10
live_merged["live_roi_percent"] = (live_merged["live_expected_value"] / 10) * 100

# Save live values
live_merged.sort_values("live_expected_value", ascending=False).to_csv("data/live_value_bets.csv", index=False)

print("✅ combine_and_rank complete with full live data integration.")
