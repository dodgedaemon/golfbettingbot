import pandas as pd
import subprocess

def run_pipeline():
    print("\n🚀 Running full model pipeline...\n")
    scripts = [
        "pull_datagolf_predictions.py",
        "pull_recent_form_scores.py",
        "pull_dg_rankings.py",
        "pull_bet365_odds.py",
        "build_course_history_score.py",
        "build_recent_form_score.py",
        "build_sg_composite_fit.py",
        "build_augusta_fit.py",
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

def show_top_predictions():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")
    print("\n🎯 Top 25 Players by Blended Model:\n")
    print(df.sort_values("final_score", ascending=False)[[
        "player_name", "country", "final_score", "your_fair_odds", "bet365_odds", "win"
    ]].head(25).to_string(index=False))

def show_top_value_bets():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")
    df = df.query("augusta_fit_score > 0 and sg_composite_fit_score > 0")
    print("\n💰 Top 25 Value Bets (With Model Input):\n")
    print(df.sort_values("expected_value", ascending=False)[[
        "player_name", "country", "expected_value", "bet365_odds", "your_fair_odds", "roi_percent"
    ]].head(25).to_string(index=False))

def inspect_player():
    df = pd.read_csv("data/ranked_predictions_with_form.csv")
    name = input("Enter full or partial player name: ").lower()
    matches = df[df["player_name"].str.lower().str.contains(name)]

    if matches.empty:
        print("❌ No matching players found.")
        return

    print(f"\n🔎 Found {len(matches)} matching player(s):\n")
    for _, row in matches.iterrows():
        print(f"🔍 Breakdown for: {row['player_name']}")
        print("-" * 50)
        print(f"🏌️  Augusta Fit Score:       {row.get('augusta_fit_score', 'N/A')}")
        print(f"📊  SG Composite Fit Score:  {row.get('sg_composite_fit_score', 'N/A')}")
        print(f"🏛️  Course History Score:    {row.get('course_history_score', 'N/A')}")
        print(f"📈  Recent Form Score:       {row.get('recent_form_score', 'N/A')}")
        print(f"💪  Driving Distance:        {row.get('driving_dist', 'N/A')}")
        print(f"🎯  Driving Accuracy:        {row.get('driving_acc', 'N/A')}")
        print(f"🧠  DataGolf Win Prob:       {round(row.get('win', 0), 5)}")
        print(f"💰  Bet365 Odds:             {row.get('bet365_odds', 'N/A')}")
        print(f"💡  Model Fair Odds:         {round(row.get('your_fair_odds', 0), 2)}")
        print(f"📊  Model Implied Prob:      {round(row.get('your_implied_prob', 0), 5)}")
        print(f"📊  Bet365 Implied Prob:     {round(row.get('bet365_implied_prob', 0), 5)}")
        print(f"⚖️  Value Delta:             {round(row.get('value_delta', 0), 5)}")
        print(f"💵  Expected Value ($10):    {round(row.get('expected_value', 0), 2)}")
        print(f"📈  ROI (%):                 {round(row.get('roi_percent', 0), 2)}%")
        print(f"🔥  Final Score:             {round(row.get('final_score', 0), 5)}")
        print("\n")


def main_menu():
    while True:
        print("""
📊 Golf Model Control Panel
0. 🔁 Run All (Full Pipeline)
1. 🎯 Show Top 25 Players by Model
2. 💰 Show Top 25 Value Bets With Model Input
3. 🕵️ Inspect a Player
4. ❌ Exit
""")
        choice = input("Select an option (0-4): ").strip()
        if choice == "0":
            run_pipeline()
        elif choice == "1":
            show_top_predictions()
        elif choice == "2":
            show_top_value_bets()
        elif choice == "3":
            inspect_player()
        elif choice == "4":
            print("👋 Exiting...")
            break
        else:
            print("⚠️ Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
