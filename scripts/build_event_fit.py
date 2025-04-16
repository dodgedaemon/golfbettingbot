import pandas as pd
import argparse
import os

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def build_event_fit(event: str, year: int, data_dir="data"):
    filename = f"historical_sg__{event.lower()}__{str(year)[-2:]}.csv"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find file: {filepath}")

    df = pd.read_csv(filepath)
    df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]

    rename_map = {
        "SG-OTT": "sg_off_the_tee",
        "SG-APP": "sg_approach",
        "SG-ATG": "sg_around_the_green",
        "SG-P": "sg_putting",
        "SG-TOT": "sg_total"
    }
    df = df.rename(columns=rename_map)

    if "Player" in df.columns:
        df["player_name"] = df["Player"].apply(normalize_name)

    sg_cols = ["sg_off_the_tee", "sg_approach", "sg_around_the_green", "sg_putting", "sg_total"]
    for col in sg_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["event_fit_score"] = df[sg_cols].mean(axis=1, skipna=True)
    df["rank"] = df["event_fit_score"].rank(ascending=False, method="min")

    # Save both archived and generic versions
    archived_name = f"{event.lower()}_sg_composite_fit_scores_{str(year)[-2:]}.csv"
    archived_path = os.path.join(data_dir, archived_name)
    df.to_csv(archived_path, index=False)

    output_path = os.path.join(data_dir, "sg_composite_fit_scores.csv")
    df.to_csv(output_path, index=False)

    print(f"✅ Saved event fit scores to:")
    print(f"   → {archived_path}")
    print(f"   → {output_path} (generic live file)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="Event name, e.g. rbc")
    parser.add_argument("--year", required=True, type=int, help="Year, e.g. 2025")
    args = parser.parse_args()

    build_event_fit(args.event, args.year)
