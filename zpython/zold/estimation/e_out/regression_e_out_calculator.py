import numpy as np
import pandas as pd

from zpython.backtest_prediction.cnn_five_year_m5_model_prediction import CnnModelPrediction
from zpython.training.e_out.error_calculation import mean_errors
from zpython.training.regression.data_preparation import read_data

predictions_to_calculate = 10000
predictor = CnnModelPrediction(bars_to_predict=predictions_to_calculate)

e_outs = pd.DataFrame(columns=["Epoch", "MSE", "RMSE", "MAE", "MAPE", "MSLE", "LogCosh", "R2"])

# Predict
predictor.to_time = predictor.from_time + pd.Timedelta(minutes=(predictor.pair.minutes() * predictions_to_calculate))
df = read_data(predictor.data_source.file_path(predictor.pair))


def e_out_for_model(model_epoch: int):
    print(f"Calculating for Epoch {model_epoch}...")
    prediction = predictor.predict(model_epoch)

    prediction_length = len(prediction.iloc[0]["prediction"])
    dates = prediction["closeTime"] + pd.Timedelta(minutes=predictor.pair.minutes())

    actual_np = np.stack([np.array(prediction.iloc[i]["prediction"]) for i in range(len(prediction))])
    expected_np = np.stack([df.loc[date:].iloc[:prediction_length]["closeBid"].values for date in dates])

    errors = mean_errors(actual_np, expected_np)
    errors["Epoch"] = model_epoch
    return errors


for epoch in range(30):
    error = e_out_for_model(epoch)
    err = pd.DataFrame.from_dict(error, orient="index").T
    e_outs = pd.concat([e_outs, err])

e_outs.to_csv(predictor.file_name_in_models_dir(f"{predictor.model_name}_losses_out.csv"), index=False)
