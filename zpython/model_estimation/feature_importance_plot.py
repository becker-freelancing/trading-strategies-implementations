import matplotlib

matplotlib.use("TkAgg")

import os

import pandas as pd

from zpython.util.path_util import from_relative_path
import matplotlib.pyplot as plt

######################################
STUDY_NAME = None


######################################

def get_names():
    if STUDY_NAME is not None:
        return [STUDY_NAME]
    return os.listdir(from_relative_path("models-bybit"))


def model_name(name):
    return name.split("_")[0]


def show(name):
    df = pd.read_csv(from_relative_path(f"models-bybit/{name}/a-feature_importance_{model_name(name)}.csv"))
    df = df.sort_values("relative_to_min_%", ascending=True)
    plt.barh(range(len(df)), df["relative_to_min_%"].values)
    plt.yticks(range(len(df)), df["feature"])
    plt.xlim((0, 100))
    plt.title(f"Feature Importance for Model {model_name(name)}")
    plt.xlabel("Importance Relative to Minimum in %")
    plt.ylabel("Feature")
    plt.grid(True, axis="x")
    plt.tight_layout()
    plt.show()


def show_plots():
    for name in get_names():
        show(name)


show_plots()
