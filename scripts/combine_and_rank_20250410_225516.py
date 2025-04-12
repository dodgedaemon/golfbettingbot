import pandas as pd
import json

# Load model weights
with open("config/model_weights.json") as f:
    weights = json.load(f)

# Load input data
preds_df = pd.read_csv("data/masters_tournament_predictions.csv")
fit_df = pd.read_csv("data/augusta_fit_scores.csv")
sg_composite_df = pd.read_csv("data/sg_composite_fit_scores.csv")
history_df = pd.read_csv("data/course_history_scores_clean.csv")
form_df = pd.read_csv("data/recent_form_scores.csv")
bet365_df = pd.read_csv("data/bet365_odds.csv")
skills_df = pd.read_csv("data/skill_ratings.csv")


# Merge data
merged = preds_df.merge(fit_df, on="player_name", how="left")
merged = merged.merge(sg_composite_df, on="player_name", how="left")
merged = merged.merge(history_df, on="player_name", how="left")
merged = merged.merge(form_df, on="player_name", how="left")
merged = merged.merge(bet365_df, on="player_name", how="left")
merged = merged.merge(
    skills_df[["player_name", "driving_dist", "driving_acc"]],
    on="player_name", how="left"
)

# Convert types and fill missing
merged["augusta_fit_score"] = merged["augusta_fit_score"].fillna(0)
merged["sg_composite_fit_score"] = merged["sg_composite_fit_score"].fillna(0)
merged["course_history_score"] = merged["course_history_score"].fillna(0)
merged["recent_form_score"] = merged["recent_form_score"].fillna(60).clip(upper=60)

merged["driving_dist"] = pd.to_numeric(merged["driving_dist"], errors="coerce").fillna(0)
merged["driving_acc"] = pd.to_numeric(merged["driving_acc"], errors="coerce").fillna(0)
merged["win"] = pd.to_numeric(merged["win"], errors="coerce")
merged["bet365_odds"] = pd.to_numeric(merged["bet365_odds"], errors="coerce")

# Final score
merged["final_score"] = (
    weights["augusta_fit_weight"] * merged["augusta_fit_score"] +
    weights["sg_composite_fit_weight"] * merged["sg_composite_fit_score"] +
    weights["course_history_weight"] * merged["course_history_score"] +
    weights["recent_form_weight"] * (60 - merged["recent_form_score"]) +
    weights["driving_dist_weight"] * merged["driving_dist"] +
    weights["driving_acc_weight"] * merged["driving_acc"]
)

# Calculate value metrics
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

# Save outputs
merged.sort_values("final_score", ascending=False).to_csv("data/ranked_predictions_with_form.csv", index=False)
merged.sort_values("final_score", ascending=False).head(10).to_csv("data/top_10_predictions_with_form.csv", index=False)
merged.sort_values("expected_value", ascending=False).to_csv("data/top_value_bets.csv", index=False)
merged.query("augusta_fit_score > 0 & course_history_score > 0") \
    .sort_values("expected_value", ascending=False) \
    .to_csv("data/top_value_bets_with_model_input.csv", index=False)

print("✅ combine_and_rank complete with driving metrics.")
