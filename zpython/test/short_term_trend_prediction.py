import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

from zpython.util import split_on_gaps
from zpython.util.data_split import train_data
from zpython.util.data_split import validation_data
from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import market_regime_to_number

def read(time_frame):
    return train.iloc[-100000:]

train, det = create_indicators(data_read_function=train_data)


def max_price_diff(x):
    x = x.values
    cumsum = np.cumsum(x)
    max_cumsum = np.max(cumsum)
    price_diff = np.exp(max_cumsum) - 1
    return price_diff


def min_price_diff(x):
    x = x.values
    cumsum = np.cumsum(x)
    max_cumsum = np.min(cumsum)
    price_diff = np.exp(max_cumsum) - 1
    return price_diff


def prepare(df):
    train_slices = []
    for slice in split_on_gaps(df, 1):
        slice = slice[~slice.index.duplicated()]
        close = slice["logReturn_closeBid_1min"]
        future_close = close.shift(-240)
        train_max_price_diff = future_close.rolling(240, min_periods=240).apply(max_price_diff).dropna()
        train_min_price_diff = future_close.rolling(240, min_periods=240).apply(min_price_diff).dropna()
        is_valid_max = train_max_price_diff[train_max_price_diff > 0.0011]
        is_valid_min = train_min_price_diff[train_min_price_diff < -0.0011]
        is_valid_max = is_valid_max.reindex(slice.index, fill_value=0)
        is_valid_min = is_valid_min.reindex(slice.index, fill_value=0)
        is_buy = (is_valid_max > abs(is_valid_min)).astype(int)
        is_sell = (is_valid_max < abs(is_valid_min)).astype(int)
        train_slices.append((slice, is_buy, is_sell))

    x_train = pd.concat([s[0] for s in train_slices])
    y_buy = pd.concat([s[1] for s in train_slices])
    y_sell = pd.concat([s[2] for s in train_slices])
    return x_train, y_buy, y_sell


val, _ = create_indicators(data_read_function=validation_data, regime_detector=det)
val["regime"] = val["regime"].apply(market_regime_to_number)
train["regime"] = train["regime"].apply(market_regime_to_number)

x_train, y_train_buy, y_train_sell = prepare(train)
x_val, y_val_buy, y_val_sell = prepare(val)

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_val = scaler.transform(x_val)

#smote = SMOTE(random_state=42)
#df_train_scaled, y_train_buy = smote.fit_resample(df_train_scaled, y_train_buy)
#df_train_scaled, y_train_sell = smote.fit_resample(df_train_scaled, y_train_sell)

# Feature verteilung
plt.hist(y_train_buy.values, label="Train (Buy)", alpha=0.1)
plt.hist(y_val_buy.values, label="Val (Buy)", alpha=0.1)
plt.hist(y_train_sell.values, label="Train (Sell)", alpha=0.1)
plt.hist(y_val_sell.values, label="Val (Sell)", alpha=0.1)
plt.legend()
plt.title("Feature verteilung")
plt.show()


# Random forest

def rand_for(x, y, x_val, y_val, buy):
    rand_for_res = pd.DataFrame(
        columns=["max_depth", "citerion", "train_acc", "train_f1", "train_tp", "train_fp", "train_tn", "train_fn",
                 "train_precision", "train_recall", "train_roc_auc",
                 "val_acc", "val_f1", "val_tp", "val_fp", "val_tn", "val_fn", "val_precision", "val_recall",
                 "val_roc_auc"])
    max_depths = list(range(2, 20, 2)) + list(range(20, 150, 10))
    criteria = ["gini", "entropy", "log_loss"]
    param_grid = [(d, c) for d in max_depths for c in criteria]

    # 🔹 Funktion, die für ein Parameterpaar trainiert & evaluiert
    def evaluate_rf(max_depth, criterion):
        try:
            print(f"Random Forest - {max_depth}, {criterion}")
            forest = RandomForestClassifier(max_depth=max_depth, criterion=criterion, random_state=42)
            forest.fit(x, y)

            # Training Metrics
            train_pred = forest.predict(x)
            train_conf = confusion_matrix(y, train_pred)
            train_metrics = {
                "train_acc": accuracy_score(y, train_pred),
                "train_f1": f1_score(y, train_pred),
                "train_tp": train_conf[1, 1],
                "train_fp": train_conf[0, 1],
                "train_tn": train_conf[0, 0],
                "train_fn": train_conf[1, 0],
                "train_precision": precision_score(y, train_pred),
                "train_recall": recall_score(y, train_pred),
                "train_roc_auc": roc_auc_score(y, train_pred),
            }

            # Validation Metrics
            val_pred = forest.predict(x_val)
            val_conf = confusion_matrix(y_val, val_pred)
            val_metrics = {
                "val_acc": accuracy_score(y_val, val_pred),
                "val_f1": f1_score(y_val, val_pred),
                "val_tp": val_conf[1, 1],
                "val_fp": val_conf[0, 1],
                "val_tn": val_conf[0, 0],
                "val_fn": val_conf[1, 0],
                "val_precision": precision_score(y_val, val_pred),
                "val_recall": recall_score(y_val, val_pred),
                "val_roc_auc": roc_auc_score(y_val, val_pred),
            }

            # Kombinieren
            return pd.DataFrame({
                "max_depth": [max_depth],
                "criterion": [criterion],
                **train_metrics,
                **val_metrics
            })
        except Exception as e:
            print(e)
            return None

    # 🔹 Parallel ausführen (n_jobs=-1 nutzt alle CPUs)
    results = Parallel(n_jobs=-1, verbose=10)(
        delayed(evaluate_rf)(d, c) for d, c in param_grid
    )
    # 🔹 Ergebnisse zusammenführen
    rand_for_res = pd.concat([r for r in results if r is not None], ignore_index=True)
    rand_for_res.to_csv(f"./rand_for_results_{'_buy' if buy else '_sell'}.csv", index=False)


rand_for(x_train, y_train_buy, x_val, y_val_buy, buy=True)
rand_for(x_train, y_train_sell, x_val, y_val_sell, buy=False)

# LightGBM
import lightgbm as lgb


def lgb_t(x, y, x_val, y_val, buy):
    lgb_res = pd.DataFrame(
        columns=["num_leaves", "max_depth", "learning_rate", "n_estimators", "min_child_samples", "train_acc",
                 "train_f1",
                 "train_tp", "train_fp", "train_tn", "train_fn", "train_precision", "train_recall", "train_roc_auc",
                 "val_acc", "val_f1", "val_tp", "val_fp", "val_tn", "val_fn", "val_precision", "val_recall",
                 "val_roc_auc"])
    param_grid = [
        (num_leaves, max_depth, lr / 100., n_est, min_child)
        for num_leaves in range(20, 100, 5)
        for max_depth in range(3, 15, 3)
        for lr in range(1, 20, 2)
        for n_est in range(100, 1000, 100)
        for min_child in [20, 50, 100]
    ]

    # 🔹 Bewertung einer Parameterkombination
    def evaluate_lgbm(num_leaves, max_depth, learning_rate, n_estimators, min_child_samples):
        try:
            print(
                f"LightGBM - leaves={num_leaves}, depth={max_depth}, lr={learning_rate}, est={n_estimators}, min_child={min_child_samples}")
            model = lgb.LGBMClassifier(
                num_leaves=num_leaves,
                max_depth=max_depth,
                learning_rate=learning_rate,
                n_estimators=n_estimators,
                min_child_samples=min_child_samples,
                random_state=42,
                n_jobs=1  # wichtig! Kein internes Parallelisieren bei Parallel-Loop
            )
            model.fit(x, y)

            train_pred = model.predict(x)
            val_pred = model.predict(x_val)

            train_conf = confusion_matrix(y, train_pred)
            val_conf = confusion_matrix(y_val, val_pred)

            result = pd.DataFrame({
                "num_leaves": [num_leaves],
                "max_depth": [max_depth],
                "learning_rate": [learning_rate],
                "n_estimators": [n_estimators],
                "min_child_samples": [min_child_samples],
                # Training
                "train_acc": [accuracy_score(y, train_pred)],
                "train_f1": [f1_score(y, train_pred)],
                "train_tp": [train_conf[1, 1]],
                "train_fp": [train_conf[0, 1]],
                "train_tn": [train_conf[0, 0]],
                "train_fn": [train_conf[1, 0]],
                "train_precision": [precision_score(y, train_pred)],
                "train_recall": [recall_score(y, train_pred)],
                "train_roc_auc": [roc_auc_score(y, train_pred)],
                # Validation
                "val_acc": [accuracy_score(y_val, val_pred)],
                "val_f1": [f1_score(y_val, val_pred)],
                "val_tp": [val_conf[1, 1]],
                "val_fp": [val_conf[0, 1]],
                "val_tn": [val_conf[0, 0]],
                "val_fn": [val_conf[1, 0]],
                "val_precision": [precision_score(y_val, val_pred)],
                "val_recall": [recall_score(y_val, val_pred)],
                "val_roc_auc": [roc_auc_score(y_val, val_pred)]
            })
            return result
        except Exception as e:
            print(e)
            return None

    # 🔹 Parallel ausführen
    results = Parallel(n_jobs=-1, verbose=10)(
        delayed(evaluate_lgbm)(*params) for params in param_grid
    )
    # 🔹 Zusammenführen
    lgb_res = pd.concat([r for r in results if r is not None], ignore_index=True)
    lgb_res.to_csv(f"./lgb{'_buy' if buy else '_sell'}.csv", index=False)


lgb_t(x_train, y_train_buy, x_val, y_val_buy, buy=True)
lgb_t(x_train, y_train_sell, x_val, y_val_sell, buy=False)

# XGBoost
import xgboost as xgb


def xgb_t(x, y, x_val, y_val, buy):
    xgb_res = pd.DataFrame(
        columns=["gamma", "max_depth", "learning_rate", "n_estimators", "min_child_weight", "train_acc", "train_f1",
                 "train_tp", "train_fp", "train_tn", "train_fn", "train_precision", "train_recall", "train_roc_auc",
                 "val_acc", "val_f1", "val_tp", "val_fp", "val_tn", "val_fn", "val_precision", "val_recall",
                 "val_roc_auc"])
    param_grid = [
        (gamma, max_depth, lr / 100., n_est, min_child)
        for gamma in [0, 1, 5, 10]
        for max_depth in [3, 5, 10, 14]
        for lr in range(1, 30, 3)
        for n_est in range(100, 1000, 100)
        for min_child in [20, 50, 100]
    ]

    # 🔹 Bewertungsfunktion
    def evaluate_xgb(gamma, max_depth, learning_rate, n_estimators, min_child_weight):
        try:
            print(
                f"XGBoost - gamma={gamma}, depth={max_depth}, lr={learning_rate}, est={n_estimators}, min_child={min_child_weight}")
            model = xgb.XGBClassifier(
                learning_rate=learning_rate,
                gamma=gamma,
                max_depth=max_depth,
                n_estimators=n_estimators,
                min_child_weight=min_child_weight,
                use_label_encoder=False,
                eval_metric="logloss",
                verbosity=0,
                n_jobs=1,  # wichtig, kein paralleles Training im Modell selbst
                random_state=42
            )
            model.fit(x, y)

            train_pred = model.predict(x)
            val_pred = model.predict(x_val)

            train_conf = confusion_matrix(y, train_pred)
            val_conf = confusion_matrix(y_val, val_pred)

            result = pd.DataFrame({
                "gamma": [gamma],
                "max_depth": [max_depth],
                "learning_rate": [learning_rate],
                "n_estimators": [n_estimators],
                "min_child_weight": [min_child_weight],
                # Training
                "train_acc": [accuracy_score(y, train_pred)],
                "train_f1": [f1_score(y, train_pred)],
                "train_tp": [train_conf[1, 1]],
                "train_fp": [train_conf[0, 1]],
                "train_tn": [train_conf[0, 0]],
                "train_fn": [train_conf[1, 0]],
                "train_precision": [precision_score(y, train_pred)],
                "train_recall": [recall_score(y, train_pred)],
                "train_roc_auc": [roc_auc_score(y, train_pred)],
                # Validation
                "val_acc": [accuracy_score(y_val, val_pred)],
                "val_f1": [f1_score(y_val, val_pred)],
                "val_tp": [val_conf[1, 1]],
                "val_fp": [val_conf[0, 1]],
                "val_tn": [val_conf[0, 0]],
                "val_fn": [val_conf[1, 0]],
                "val_precision": [precision_score(y_val, val_pred)],
                "val_recall": [recall_score(y_val, val_pred)],
                "val_roc_auc": [roc_auc_score(y_val, val_pred)]
            })
            return result
        except Exception as e:
            print(e)
            return None

    # 🔹 Parallel ausführen
    results = Parallel(n_jobs=-1, verbose=10)(
        delayed(evaluate_xgb)(*params) for params in param_grid
    )
    # 🔹 Zusammenführen
    xgb_res = pd.concat([r for r in results if r is not None], ignore_index=True)
    xgb_res.to_csv(f"./xgb{'_buy' if buy else '_sell'}.csv", index=False)


xgb_t(x_train, y_train_buy, x_val, y_val_buy, buy=True)
xgb_t(x_train, y_train_sell, x_val, y_val_sell, buy=False)
