import matplotlib
import pandas as pd

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np

# CSV-Datei laden
df = pd.read_csv("./errors.csv")

# Für jedes Modell separat plotten
for model in np.unique(df["Model"].values):
    model_df = df[df["Model"] == model]

    for tf in np.unique(model_df["TimeFrame"].values):
        tf_df = model_df[model_df["TimeFrame"] == tf]
        X = tf_df["InputLength"].values
        Y = tf_df["RMSE"].values

        X_min = X[np.argmin(Y)]
        Y_min = np.min(Y)

        plt.scatter(X_min, Y_min, label=f"Min für M{tf} (X={X_min}, Y={Y_min:.5f})")
        plt.plot(X, Y, label=f"TimeFrame M{tf}")

    plt.title(f"Model: {model}")
    plt.xlabel("Input Length")
    plt.ylabel("RMSE")
    plt.legend()
    plt.show()
