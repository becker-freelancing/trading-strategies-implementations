import matplotlib
import pandas as pd

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np

# CSV-Datei laden
df = pd.read_csv("./errors_2.csv")

# Für jedes Modell separat plotten
for model in np.unique(df["Model"].values):
    model_df = df[df["Model"] == model]

    for tf, color in zip(np.unique(model_df["TimeFrame"].values),
                         ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]):
        tf_df = model_df[model_df["TimeFrame"] == tf]
        group = tf_df[["InputLength", "RMSE_TRAIN", "RMSE_TEST"]].groupby("InputLength").mean()
        X = group.index
        Y_train = group["RMSE_TRAIN"].values
        Y_test = group["RMSE_TEST"].values

        X_min_train = X[np.argmin(Y_train)]
        Y_min_train = np.min(Y_train)
        X_min_test = X[np.argmin(Y_test)]
        Y_min_test = np.min(Y_test)

        plt.scatter(X_min_train, Y_min_train, label=f"Train Min für M{tf} (X={X_min_train}, Y={Y_min_train:.5f})",
                    color=color)
        plt.plot(X, Y_train, label=f"TimeFrame M{tf}", color=color)
        plt.scatter(X_min_test, Y_min_test, label=f"Test Min für M{tf} (X={X_min_test}, Y={Y_min_test:.5f})",
                    color=color)
        plt.plot(X, Y_test, "--", label=f"TimeFrame M{tf}", color=color)

    plt.title(f"Model: {model}")
    plt.xlabel("Input Length")
    plt.ylabel("RMSE")
    plt.yscale("log")
    plt.legend()
    plt.show()
