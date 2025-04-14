import pandas as pd
import requests
from pathlib import Path

# Constants
INPUT_CSV = Path("data/datagolf_endpoints.csv")
OUTPUT_CSV = Path("data/datagolf_access_results.csv")
TIMEOUT = 10  # seconds

# Load your list of endpoints
df = pd.read_csv(INPUT_CSV)

# Keep only one full_url per unique base_url
unique_endpoints = df.drop_duplicates(subset="base_url")

results = []

print(f"🔍 Testing {len(unique_endpoints)} unique endpoints...")

for _, row in unique_endpoints.iterrows():
    base_url = row["base_url"]
    test_url = row["full_url"]

    try:
        response = requests.get(test_url, timeout=TIMEOUT)
        status_code = response.status_code
        if status_code == 200:
            status = "✅ Success"
            notes = "Accessible"
        elif status_code == 403:
            status = "❌ Forbidden"
            notes = "Requires upgraded subscription"
        else:
            status = "⚠️ Error"
            notes = f"Status {status_code}"
    except requests.RequestException as e:
        status = "❌ Failed"
        status_code = "N/A"
        notes = str(e)

    print(f"{base_url}: {status} ({status_code})")

    results.append({
        "base_url": base_url,
        "tested_url": test_url,
        "status": status,
        "status_code": status_code,
        "notes": notes
    })

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv(OUTPUT_CSV, index=False)
print(f"\n✅ Saved results to {OUTPUT_CSV}")
