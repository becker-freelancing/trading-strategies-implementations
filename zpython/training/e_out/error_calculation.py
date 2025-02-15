import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.metrics import precision_recall_fscore_support


def mean_errors(array1: np.ndarray, array2: np.ndarray) -> dict:
    """
    Berechnet verschiedene Fehlermaße zwischen zwei Nx30 numpy Arrays.

    :param array1: Erstes Nx30 numpy Array
    :param array2: Zweites Nx30 numpy Array
    :return: Ein Dictionary mit MSE, RMSE, MAE, MAPE, MSLE, LogCosh und R2
    """
    if array1.shape != array2.shape:
        raise ValueError("Die Eingabe-Arrays müssen die gleiche Form haben.")

    mae = np.mean(np.abs(array1 - array2))
    mse = mean_squared_error(array1, array2)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((array1 - array2) / array1)) * 100
    msle = mean_squared_error(np.log1p(array1), np.log1p(array2))
    log_cosh = np.mean(np.log(np.cosh(array1 - array2)))
    r2 = r2_score(array1, array2)

    return {"MAE": mae, "MSE": mse, "RMSE": rmse, "MAPE": mape, "MSLE": msle, "LogCosh": log_cosh, "R2": r2}


def classification_mean_errors(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    crossentropy = np.mean(-np.sum(y_true * np.log(y_pred.astype(float)), axis=1))

    # Berechnung der kategorischen Genauigkeit
    y_true_class = np.argmax(y_true, axis=1)  # Index der echten Klasse (maximale Wahrscheinlichkeit)
    y_pred_class = np.argmax(y_pred, axis=1)  # Index der vorhergesagten Klasse (maximale Wahrscheinlichkeit)
    # Genauigkeit berechnen: Vergleich der echten Klasse mit der vorhergesagten Klasse
    accuracy = np.mean(y_true_class == y_pred_class)

    # Berechnung von Precision, Recall und F1-Score für jede Klasse
    precision, recall, f1_score, _ = precision_recall_fscore_support(y_true_class, y_pred_class, average=None)
    f1_score = [float(f) for f in f1_score]
    return {
        "Categorial_Crossentropy": crossentropy,
        "Categorical_Accuracy": accuracy,
        "F1_Score": f1_score
    }
