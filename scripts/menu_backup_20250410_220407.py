import pandas as pd

# Load main predictions file once
df = pd.read_csv("data/ranked_predictions_with_form.csv")

def show_top_predictions():
    print("\n🎯 Top 25 Players by Blended Model:\n")
    print(df.sort_values("final_score", ascending=False)[[
        "player_name", "country", "final_score", "your_fair_odds", "bet365_odds", "win"
    ]].head(25).to_string(index=False))

def show_top_value_bets():
    print("\n💰 Top 25 Value Bets (With Model Input):\n")
    filtered = df[
        (df["augusta_fit_score"] > 0) & 
        (df["sg_composite_fit_score"] > 0)
    ]
    print(filtered.sort_values("expected_value", ascending=False)[[
        "player_name", "country", "expected_value", "bet365_odds", "your_fair_odds", "roi_percent"
    ]].head(25).to_string(index=False))


def inspect_player():
    name = input("Enter player name (e.g., Scottie Scheffler): ").strip()
    row = df[df["player_name"].str.lower() == name.lower()]

    if row.empty:
        print("🚫 Player not found.")
    else:
        row = row.iloc[0]
        print(f"\n🔍 Breakdown for: {row['player_name']}")
        print("-" * 50)
        print(f"🌍 Country:                  {row.get('country', 'N/A')}")
        print(f"🏌️  Augusta Fit Score:       {row['augusta_fit_score']:.3f}")
        print(f"📊  SG Composite Fit Score:  {row.get('sg_composite_fit_score', 'N/A'):.3f}")
        print(f"🏛️  Course History Score:    {row['course_history_score']:.3f}")
        print(f"📈  Recent Form Score:       {row['recent_form_score']:.2f}")
        print(f"📏  Driving Distance:        {row.get('driving_dist', 'N/A')}")
        print(f"🎯  Driving Accuracy:        {row.get('driving_acc', 'N/A')}")
        print(f"🧠  DataGolf Win Prob:       {round(1 / row['win'], 5) if row['win'] > 0 else 'N/A'}")
        print(f"📊  DataGolf Model Win Odds: {row['win']}")
        print(f"💡  Model Fair Odds:         {row['your_fair_odds']:.2f}")
        print(f"💰  Bet365 Odds:             {row['bet365_odds']}")
        print(f"📊  Model Implied Prob:      {row['your_implied_prob']:.5f}")
        print(f"📊  Bet365 Implied Prob:     {row['bet365_implied_prob']:.5f}")
        print(f"⚖️  Value Delta:             {row['value_delta']:.5f}")
        print(f"💵  Expected Value ($10):    {row['expected_value']:.2f}")
        print(f"📈  ROI (%):                 {row['roi_percent']:.2f}%")
        print(f"🎯 Final Score:              {row['final_score']:.5f}")

def main_menu():
    while True:
        print("""
📊 Golf Model Control Panel
1. 🎯 Show Top 25 Players by Model
2. 💰 Show Top 25 Value Bets With Model Input
3. 🕵️ Inspect a Player
4. ❌ Exit
""")
        choice = input("Select an option (1-4): ").strip()
        if choice == "1":
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
