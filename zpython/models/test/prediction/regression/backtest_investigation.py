import pandas as pd

df = pd.read_csv("./backtest_results_ratios.csv")

filtered = df[df["ExpectedNoneRatio"] < 0.5]

print(filtered)
