import json
from pathlib import Path

CONFIG_DIR = Path("config")
DATA_DIR = Path("data")

def load_weights():
    # Read current event from meta file
    with open(DATA_DIR / "event_meta.json", "r") as f:
        meta = json.load(f)

    event = meta["event"]
    weights_file = CONFIG_DIR / f"model_weights_{event}.json"

    if not weights_file.exists():
        raise FileNotFoundError(f"❌ No weights file found for event: {event}")

    with open(weights_file, "r") as f:
        weights = json.load(f)

    return weights

if __name__ == "__main__":
    weights = load_weights()
    print("🎯 Loaded weights:")
    for k, v in weights.items():
        print(f"{k}: {v}")
