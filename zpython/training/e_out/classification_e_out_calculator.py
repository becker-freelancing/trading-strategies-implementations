import numpy as np
import pandas as pd

from zpython.prediction.classification.classification_limit_30_stop_10 import ClassificationLimit30Stop10
from zpython.training.classification.classification_limit_30_stop_10 import ClassificationLimit30Stop10Training
from zpython.training.e_out.error_calculation import classification_mean_errors

predictions_to_calculate = 1000
predictor = ClassificationLimit30Stop10(bars_to_predict=predictions_to_calculate)
training = ClassificationLimit30Stop10Training()

if training.model_name != predictor.model_name:
    raise Exception()

e_outs = pd.DataFrame(columns=["Epoch", "Categorial_Crossentropy", "Categorical_Accuracy", "F1_Score"])

# Predict
predictor.to_time = predictor.from_time + pd.Timedelta(minutes=(predictor.pair.minutes() * predictions_to_calculate))
df = training.read_raw_expected()


def e_out_for_model(model_epoch: int):
    print(f"Calculating for Epoch {model_epoch}...")
    prediction = predictor.predict(model_epoch)

    dates = prediction["closeTime"] + pd.Timedelta(minutes=predictor.pair.minutes())

    actual_np = np.vstack([prediction.iloc[i][predictor.output_labels()].to_numpy() for i in range(len(prediction))])
    expected_np = df.loc[dates][predictor.output_labels()].to_numpy()

    errors = classification_mean_errors(expected_np, actual_np)
    errors["Epoch"] = model_epoch
    return errors


try:
    for epoch in range(30):
        error = e_out_for_model(epoch)
        err = pd.DataFrame.from_dict(error, orient="index").T
        e_outs = pd.concat([e_outs, err])
except Exception:
    pass

e_outs.to_csv(predictor.file_name_in_models_dir(f"{predictor.model_name}_losses_out.csv"), index=False)
