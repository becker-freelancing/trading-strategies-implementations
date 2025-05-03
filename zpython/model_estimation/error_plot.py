import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio

from zpython.util.path_util import from_relative_path

pio.renderers.default = 'browser'
import numpy as np

##################### Constants

MODEL_NAME = "multiscalecnn"
FORMATTED_MODEL_NAME = "Multi-Scale-CNN"
STUDY_NAME = "2025-04-30_07-02-07"

COL_MAPPING = {
    "input_length": "Input Length",
    "num_units": "No. Units",
    "num_units_cnn": "No. Units CNN",
    "kernel_size": "Kernel Size",
    "pool_size": "Pool Size",
    "learning_rate": "Learning Rate",
    "val_root_mean_squared_error": "Validation RMSE"
}

###############################

metrics_path = from_relative_path(f"models-bybit/{MODEL_NAME}_{STUDY_NAME}/a-metrics_{MODEL_NAME}.csv")
metrics = pd.read_csv(metrics_path)

trials_path = from_relative_path(f"models-bybit/{MODEL_NAME}_{STUDY_NAME}/a-trials_{MODEL_NAME}.csv")
trials = pd.read_csv(trials_path, quotechar='(', dtype=str)

trials = trials.drop(["x_train_shape", "y_train_shape", "x_val_shape", "y_val_shape"], axis=1)
for col in trials.columns:
    trials[col] = trials[col].apply(eval)
trials.set_index("trial", inplace=True)

best_metrics = metrics.loc[metrics.groupby("trial")["val_root_mean_squared_error"].idxmin()]
join = best_metrics.join(trials, on="trial")
join = join.drop([
    "epoch",
    "mean_squared_error",
    "root_mean_squared_error",
    "mean_absolute_error",
    "mean_absolute_percentage_error",
    "mean_squared_logarithmic_error",
    "logcosh",
    "r2_score",
    "val_mean_squared_error",
    "val_mean_absolute_error",
    "val_mean_absolute_percentage_error",
    "val_mean_squared_logarithmic_error",
    "val_logcosh",
    "val_r2_score"
], axis=1)
val_root_mean_squared_error = join["val_root_mean_squared_error"]
join = join.drop(["val_root_mean_squared_error"], axis=1)
join = join[join.var().sort_values(ascending=False).index]
join = join.join(val_root_mean_squared_error)

top_n = 3
top_positions = join['val_root_mean_squared_error'].argsort().values[:top_n]

# Farbwerte erzeugen: 1 (grün) für Top-3, 0 (blau) für alle anderen
color_values = np.zeros(len(join))
color_values[top_positions] = 1  # 1 = grün, 0 = blau

fig = go.Figure(
    data=go.Parcoords(
        line=dict(
            color=color_values,
            colorscale=[[0, 'blue'], [1, 'orange']],
            cmin=0,
            cmax=1,
            showscale=False
        ),
        dimensions=[
            dict(label=COL_MAPPING[col], values=join[col])
            for col in join.columns if col != "trial"
        ],
        name="Test"
    )
)
fig.update_layout(
    title_text=f"Trial Parameters for Model {FORMATTED_MODEL_NAME}",  # Der korrekte Schlüssel
    title_x=0.5,  # Zentrieren des Titels
    title_xanchor='center'  # Verankerung des Titels
)

fig.show()
