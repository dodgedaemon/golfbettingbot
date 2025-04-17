from pathlib import Path
import pandas as pd
import json
import os

def get_current_event_and_year(meta_path="data/event_meta.json"):
    with open(meta_path, "r") as f:
        meta = json.load(f)
    return meta["event"], meta["year"]

def normalize_name(name):
    parts = name.split(",")
    return parts[1].strip() + " " + parts[0].strip() if len(parts) == 2 else name.strip()

def build_event_fit(event: str, year: int, data_dir="data"):
    # Load weights
    weights_path = f"config/model_weights_{event}.json"
    with open(weights_path, "r") as f:
        model_weights = json.load(f)

    component_weights = model_weights.get("event_fit_components", {})
    filename = f"historical_sg_{event}_{str(year)[-2:]}.csv"
    filepath = os.path.join(data_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find file: {filepath}")

    df = pd.read_csv(filepath)
    df.columns = [col.strip().replace("\ufeff", "").lower() for col in df.columns]

    # Optional rename map for readability
    rename_map = {
        "sg-ott": "sg_ott",
        "sg-app": "sg_app",
        "sg-atg": "sg_atg",
        "sg-p": "sg_putt",
        "sg-t2g": "sg_t2g",
        "sg-bst": "sg_bst",
        "sg-tot": "sg_total"
    }
    df = df.rename(columns=rename_map)

    if "player" in df.columns:
        df["player_name"] = df["player"].apply(normalize_name)

    for key in component_weights:
        if key not in df.columns:
            df[key] = 0.0
        df[key] = pd.to_numeric(df[key], errors="coerce").fillna(0)

    df["event_fit_score"] = df.apply(
        lambda row: sum(row[k] * w for k, w in component_weights.items()), axis=1
    )
    df["rank"] = df["event_fit_score"].rank(ascending=False, method="min")

    archived_name = f"{event}_sg_composite_fit_scores_{str(year)[-2:]}.csv"
    archived_path = os.path.join(data_dir, archived_name)
    output_path = os.path.join(data_dir, "sg_composite_fit_scores.csv")

    df_out = df[["player_name", "event_fit_score", "rank"]]
    df_out.to_csv(archived_path, index=False)
    df_out.to_csv(output_path, index=False)

    print(f"✅ Saved event fit scores to:")
    print(f"   → {archived_path}")
    print(f"   → {output_path} (generic live file)")

if __name__ == "__main__":
    event, year = get_current_event_and_year()
    print(f"🔧 Building event fit for: {event} ({year})")
    build_event_fit(event, year)
