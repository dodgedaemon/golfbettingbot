import pandas as pd
import subprocess
import json

def run_pipeline():
    print("\n🚀 Running full model pipeline...\n")
    scripts = [
        "pull_datagolf_predictions.py",
        "pull_recent_form_scores.py",
        "pull_dg_rankings.py",
        "pull_bet365_odds.py",
        "pull_live_predictions.py",
        # "pull_live_odds.py",
        "build_course_history_score.py",
        "build_recent_form_score.py",
        "build_sg_composite_fit.py",
        "build_event_fit.py",
        "combine_and_rank.py"
    ]

    for script in scripts:
        print(f"▶️ Running: {script}")
        result = subprocess.run(["python", f"scripts/{script}"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Error in {script}:")
            print(result.stderr)
            return

    print("✅ Pipeline completed successfully.")
    show_top_predictions()
    show_top_value_bets()
    show_live_value_bets()

def show_top_predictions():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")
    # Sort by final_score in descending order before adding the 'Number' column
    df = df.sort_values("final_score", ascending=False)
    # Add a 'Number' column with incremental values (starting from 1)
    df['Number'] = range(1, len(df) + 1)
    print("\n🎯 Top 25 Players by Blended Model:\n")
    # Display the 'Number' column alongside other selected columns
    print(df[[
        "Number", "player_name", "country", "datagolf_rank", "final_score",
        "your_fair_odds", "bet365_odds", "win"
    ]].head(25).to_string(index=False))

def show_top_value_bets():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")
    # Filter for event_fit_score > 0 before sorting
    if "event_fit_score" in df.columns:
        df = df[df["event_fit_score"] > 0]
    # Sort by expected_value in descending order before adding the 'Number' column
    df = df.sort_values("expected_value", ascending=False)
    # Add a 'Number' column with incremental values (starting from 1)
    df['Number'] = range(1, len(df) + 1)
    print("\n💰 Top 25 Value Bets (With Model Input):\n")
    # Display the 'Number' column alongside other selected columns
    print(df[[
        "Number", "player_name", "country", "datagolf_rank",
        "expected_value", "bet365_odds", "your_fair_odds", "roi_percent"
    ]].head(25).to_string(index=False))

def show_live_value_bets():
    df = pd.read_csv("data/live_value_bets.csv")
    # Filter for win_live > 0 before sorting
    df = df[df["win_live"] > 0]
    # Sort by live_expected_value in descending order before adding the 'Number' column
    df = df.sort_values("live_expected_value", ascending=False)
    # Add a 'Number' column with incremental values (starting from 1)
    df['Number'] = range(1, len(df) + 1)
    print("\n📡 Top 25 Live Value Bets (With Live Win %, Live Odds, and Current Position):\n")
    # Display the 'Number' column alongside other selected columns
    print(df[[
        "Number", "player_name", "country", "datagolf_rank", "round", "thru", "today",
        "current_score", "current_pos", "live_expected_value", "live_betfair_odds",
        "live_your_fair_odds", "live_roi_percent"
    ]].head(25).to_string(index=False))



def inspect_player():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")

    # Load event metadata and weights
    with open("data/event_meta.json") as f:
        event_meta = json.load(f)
    weights_path = f"config/model_weights_{event_meta['event']}.json"
    with open(weights_path) as f:
        weights = json.load(f)

    name = input("Enter full or partial player name: ").lower()
    matches = df[df["player_name"].str.lower().str.contains(name)]

    if matches.empty:
        print("❌ No matching players found.")
        return

    print(f"\n🔎 Found {len(matches)} matching player(s):\n")

    for _, row in matches.iterrows():
        print(f"🔍 Breakdown for: {row['player_name']}")
        print("-" * 50)

        # Base metrics
        print(f"🏟️  Event Fit Score:         {row.get('event_fit_score', 'N/A')}")
        print(f"📜  Course History Score:    {row.get('course_history_score', 'N/A')}")
        print(f"📈  Recent Form Score:       {row.get('recent_form_score', 'N/A')}")
        print(f"💪  Driving Distance (Adj.): {row.get('driving_dist', 'N/A')}")
        print(f"🎯  Driving Accuracy (Adj.): {row.get('driving_acc', 'N/A')}")

        # Breakdown of event fit components
        event_fields = ["sg_ott", "sg_app", "sg_atg", "sg_putt", "sg_t2g", "sg_bst", "driving_dist", "driving_acc"]
        if "event_fit_components" in weights and all(field in df.columns for field in event_fields):
            print("\n🧮 Event Fit Score Breakdown:")
            for stat in event_fields:
                weight = weights["event_fit_components"].get(stat, 0)
                value = row.get(stat, 0)
                print(f"  ▶️ {stat.upper()} ({weight} × {value}) = {weight * value:.3f}")

        # Model score formula (for both current and event fit scores)
        print("\n🧮 Model Score Calculation:")
        ef = row.get("event_fit_score", 0)
        sg = row.get("sg_composite_fit_score", 0)
        ch = row.get("course_history_score", 0)
        dd = row.get("driving_dist", 0)
        da = row.get("driving_acc", 0)
        scf = row.get("sg_current_form_score", 0)

        print(f"  ▶️ Event Fit ({weights['event_fit_score_weight']} × {ef}) = {weights['event_fit_score_weight'] * ef:.3f}")
        print(f"  ▶️ SG Current Form ({weights['sg_current_form_score_weight']} × {scf}) = {weights['sg_current_form_score_weight'] * scf:.3f}")
        print(f"  ▶️ Course History ({weights['course_history_score_weight']} × {ch}) = {weights['course_history_score_weight'] * ch:.3f}")

        # Driving distance and accuracy weights are now taken from event_fit_components
        driving_dist_weight = weights["event_fit_components"].get("driving_dist", 0)
        driving_acc_weight = weights["event_fit_components"].get("driving_acc", 0)

        print(f"  ▶️ Driving Dist. ({driving_dist_weight} × {dd}) = {driving_dist_weight * dd:.3f}")
        print(f"  ▶️ Driving Acc. ({driving_acc_weight} × {da}) = {driving_acc_weight * da:.3f}")
        
        print(f"  🧠 Combined Model Score: {row.get('your_model_score', 'N/A'):.5f}")

        # Market comparison
        print(f"\n🌍  DataGolf Rank:           {row.get('datagolf_rank', 'N/A')}")
        print(f"🧠  DataGolf Win Probability: {round(row.get('win', 0), 5)}")
        print(f"💰  Bet365 Odds:             {row.get('bet365_odds', 'N/A')}")
        print(f"🎯  Model Fair Odds:         {round(row.get('your_fair_odds', 0), 2)}")
        print(f"📊  Model Implied Prob:      {round(row.get('your_implied_prob', 0), 5)}")
        print(f"📊  Bet365 Implied Prob:     {round(row.get('bet365_implied_prob', 0), 5)}")
        print(f"⚖️  Value Delta:             {round(row.get('value_delta', 0), 5)}")
        print(f"💵  Expected Value ($10):    {round(row.get('expected_value', 0), 2)}")
        print(f"📈  ROI (%):                 {round(row.get('roi_percent', 0), 2)}%")
        print("\n")

def compare_players():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")

    # Load event metadata and weights
    with open("data/event_meta.json") as f:
        event_meta = json.load(f)
    weights_path = f"config/model_weights_{event_meta['event']}.json"
    with open(weights_path) as f:
        weights = json.load(f)

    # Specify player names for comparison
    players = ['Scottie Scheffler', 'Ludvig Aberg']

    # Filter the dataframe for the specified players
    matches = df[df["player_name"].isin(players)]

    if matches.empty:
        print("❌ No matching players found.")
        return

    print(f"\n🔎 Comparing Players:\n")
    print("-" * 50)

    for _, row in matches.iterrows():
        print(f"🔍 Breakdown for: {row['player_name']}")
        print("-" * 50)

        # Base metrics
        print(f"🏟️  Event Fit Score:         {row.get('event_fit_score', 'N/A')}")
        print(f"📜  Course History Score:    {row.get('course_history_score', 'N/A')}")
        print(f"📈  SG Current Form Score:   {row.get('sg_current_form_score', 'N/A')}")
        print(f"💪  Driving Distance (Adj.): {row.get('driving_dist', 'N/A')}")
        print(f"🎯  Driving Accuracy (Adj.): {row.get('driving_acc', 'N/A')}")

        # Breakdown of event fit components
        event_fields = ["sg_ott", "sg_app", "sg_atg", "sg_putt", "sg_t2g", "sg_bst", "driving_dist", "driving_acc"]
        if "event_fit_components" in weights and all(field in df.columns for field in event_fields):
            print("\n🧮 Event Fit Score Breakdown:")
            for stat in event_fields:
                weight = weights["event_fit_components"].get(stat, 0)
                value = row.get(stat, 0)
                print(f"  ▶️ {stat.upper()} ({weight} × {value}) = {weight * value:.3f}")

        # Model score formula (for both current and event fit scores)
        print("\n🧮 Model Score Calculation:")
        ef = row.get("event_fit_score", 0)
        sg = row.get("sg_composite_fit_score", 0)
        ch = row.get("course_history_score", 0)
        dd = row.get("driving_dist", 0)
        da = row.get("driving_acc", 0)
        scf = row.get("sg_current_form_score", 0)

        # Calculate and display the weighted contributions
        print(f"  ▶️ Event Fit ({weights['event_fit_score_weight']} × {ef}) = {weights['event_fit_score_weight'] * ef:.3f}")
        print(f"  ▶️ SG Current Form ({weights['sg_current_form_score_weight']} × {scf}) = {weights['sg_current_form_score_weight'] * scf:.3f}")
        print(f"  ▶️ Course History ({weights['course_history_score_weight']} × {ch}) = {weights['course_history_score_weight'] * ch:.3f}")

        # Driving distance and accuracy weights from event_fit_components
        driving_dist_weight = weights["event_fit_components"].get("driving_dist", 0)
        driving_acc_weight = weights["event_fit_components"].get("driving_acc", 0)

        print(f"  ▶️ Driving Dist. ({driving_dist_weight} × {dd}) = {driving_dist_weight * dd:.3f}")
        print(f"  ▶️ Driving Acc. ({driving_acc_weight} × {da}) = {driving_acc_weight * da:.3f}")
        
        print(f"  🧠 Combined Model Score: {row.get('your_model_score', 'N/A'):.5f}")
        print("\n" + "-" * 50)

def main_menu():
    while True:
        print("""
📊 Golf Model Control Panel
0. 🔁 Run All (Full Pipeline)
1. 🎯 Show Top 25 Players by Model
2. 💰 Show Top 25 Value Bets With Model Input
3. 🕵️ Inspect a Player
4. 📡 Show Live Value Bets (Using Live Win Prediction)
5. 🔄 Compare Players (Scottie vs Ludvig)
6. ❌ Exit
""")
        choice = input("Select an option (0-6): ").strip()
        if choice == "0":
            run_pipeline()
        elif choice == "1":
            show_top_predictions()
        elif choice == "2":
            show_top_value_bets()
        elif choice == "3":
            inspect_player()
        elif choice == "4":
            show_live_value_bets()
        elif choice == "5":
            compare_players()  # new option for comparison
        elif choice == "6":
            print("👋 Exiting...")
            break
        else:
            print("⚠️ Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
