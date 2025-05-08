import pandas as pd

from zpython.util.data_split import valid_time_frames
from zpython.util.path_util import from_relative_path


def interpret(time_frame):
    print("=" * 100)
    print(f"= Interpreting M{time_frame}")
    print("=" * 100)

    N_BEST = 30

    df = pd.read_csv(from_relative_path(f"analysis-bybit/granger/granger_test_{time_frame}.csv"))

    caused = {}  # Map<CausedLag, Map<Causing, List<[CausingLag, pValue]>>>
    best = {}

    for lag in range(30):

        print(f"\tLag: {lag}")
        lag_select = df[df["caused_lag"] == lag]

        causings = {}

        for id, row in lag_select.iterrows():
            signif_lags = eval(row["signif_lags"])
            causing = eval(row["causing"])[0]
            causings[causing] = []

            for causing_lag in signif_lags:
                if causing_lag[1] < 0.05:
                    causings[causing].append(causing_lag)

        best_for_lag = {}
        last_best = 0
        for i in range(N_BEST):
            best_p = 100000
            best_causing = None
            best_causing_lag = None
            for k in causings.keys():
                v = causings[k]
                for l in v:
                    if best_p > l[1] > last_best:
                        best_p = l[1]
                        best_causing = k
                        best_causing_lag = l[0]

            last_best = best_p
            best_for_lag[f"Best_{i}"] = [best_causing, best_causing_lag, best_p]
            print(f"\t\t\t* Causing: {best_causing}\tCausing lag: {best_causing_lag}\tp-Value: {best_p}")

        best[f"CausedLag_{lag}"] = best_for_lag
        caused[lag] = causings

    write_path = from_relative_path(f"analysis-bybit/granger/granger_test_{time_frame}_analysis.csv")
    best_df = pd.DataFrame(best)
    best_df.reset_index(inplace=True)
    best_df.to_csv(write_path, index=False)


for i in valid_time_frames():
    interpret(i)
