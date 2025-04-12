import pandas as pd

df = pd.read_csv("data/sg_augusta.csv")
df.to_csv("data/augusta_fit_scores.csv", index=False)
print("✅ augusta_fit_scores.csv created from sg_augusta.csv")
