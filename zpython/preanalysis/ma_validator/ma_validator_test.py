import pandas as pd
from joblib import Parallel, delayed
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

from zpython.util.data_split import validation_data
from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import market_regime_to_number
from zpython.util.path_util import from_relative_path

# Daten laden
res_train = pd.read_csv(from_relative_path("ai-data/2_MA_Strategy/2_MA_Strategy_TRAIN.csv"), delimiter=";")
res_train["openTime"] = pd.to_datetime(res_train["openTime"])
res_val = pd.read_csv(from_relative_path("ai-data/2_MA_Strategy/2_MA_Strategy_VAL.csv"), delimiter=";")
res_val["openTime"] = pd.to_datetime(res_val["openTime"])

df_train = create_indicators()[0]
df_val = create_indicators(validation_data)[0]

df_train = df_train.loc[res_train["openTime"].values]
df_val = df_val.loc[res_val["openTime"].values]
df_train["regime"] = df_train["regime"].apply(market_regime_to_number)
df_val["regime"] = df_val["regime"].apply(market_regime_to_number)

# Skalieren
scaler = StandardScaler()
df_train_scaled = scaler.fit_transform(df_train)
df_val_scaled = scaler.transform(df_val)

# Features erstellen
y_train = (res_train["profitInEurosWithFees"] > 0).astype(int)
y_val = (res_val["profitInEurosWithFees"] > 0).astype(int)

# Feature verteilung
# plt.hist(y_train.values, label="Train")
# plt.hist(y_val.values, label="Val")
# plt.legend()
# plt.title("Feature verteilung")
# plt.show()

# Random forest

rand_for_res = pd.DataFrame(
    columns=["max_depth", "citerion", "train_acc", "train_f1", "train_tp", "train_fp", "train_tn", "train_fn",
             "train_precision", "train_recall", "train_roc_auc",
             "val_acc", "val_f1", "val_tp", "val_fp", "val_tn", "val_fn", "val_precision", "val_recall", "val_roc_auc"])

max_depths = list(range(2, 20, 1)) + list(range(20, 150, 5))
criteria = ["gini", "entropy", "log_loss"]
param_grid = [(d, c) for d in max_depths for c in criteria]


# 🔹 Funktion, die für ein Parameterpaar trainiert & evaluiert
def evaluate_rf(max_depth, criterion):
    try:
        print(f"Random Forest - {max_depth}, {criterion}")
        forest = RandomForestClassifier(max_depth=max_depth, criterion=criterion, random_state=42)
        forest.fit(df_train_scaled, y_train)

        # Training Metrics
        train_pred = forest.predict(df_train_scaled)
        train_conf = confusion_matrix(y_train, train_pred)
        train_metrics = {
            "train_acc": accuracy_score(y_train, train_pred),
            "train_f1": f1_score(y_train, train_pred),
            "train_tp": train_conf[1, 1],
            "train_fp": train_conf[0, 1],
            "train_tn": train_conf[0, 0],
            "train_fn": train_conf[1, 0],
            "train_precision": precision_score(y_train, train_pred),
            "train_recall": recall_score(y_train, train_pred),
            "train_roc_auc": roc_auc_score(y_train, train_pred),
        }

        # Validation Metrics
        val_pred = forest.predict(df_val_scaled)
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

rand_for_res.to_csv("./rand_for_results.csv", index=False)

# LightGBM
import lightgbm as lgb

lgb_res = pd.DataFrame(
    columns=["num_leaves", "max_depth", "learning_rate", "n_estimators", "min_child_samples", "train_acc", "train_f1",
             "train_tp", "train_fp", "train_tn", "train_fn", "train_precision", "train_recall", "train_roc_auc",
             "val_acc", "val_f1", "val_tp", "val_fp", "val_tn", "val_fn", "val_precision", "val_recall", "val_roc_auc"])

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
        model.fit(df_train_scaled, y_train)

        train_pred = model.predict(df_train_scaled)
        val_pred = model.predict(df_val_scaled)

        train_conf = confusion_matrix(y_train, train_pred)
        val_conf = confusion_matrix(y_val, val_pred)

        result = pd.DataFrame({
            "num_leaves": [num_leaves],
            "max_depth": [max_depth],
            "learning_rate": [learning_rate],
            "n_estimators": [n_estimators],
            "min_child_samples": [min_child_samples],
            # Training
            "train_acc": [accuracy_score(y_train, train_pred)],
            "train_f1": [f1_score(y_train, train_pred)],
            "train_tp": [train_conf[1, 1]],
            "train_fp": [train_conf[0, 1]],
            "train_tn": [train_conf[0, 0]],
            "train_fn": [train_conf[1, 0]],
            "train_precision": [precision_score(y_train, train_pred)],
            "train_recall": [recall_score(y_train, train_pred)],
            "train_roc_auc": [roc_auc_score(y_train, train_pred)],
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

lgb_res.to_csv("./lgb.csv", index=False)

# XGBoost
import xgboost as xgb

xgb_res = pd.DataFrame(
    columns=["gamma", "max_depth", "learning_rate", "n_estimators", "min_child_weight", "train_acc", "train_f1",
             "train_tp", "train_fp", "train_tn", "train_fn", "train_precision", "train_recall", "train_roc_auc",
             "val_acc", "val_f1", "val_tp", "val_fp", "val_tn", "val_fn", "val_precision", "val_recall", "val_roc_auc"])

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
        model.fit(df_train_scaled, y_train)

        train_pred = model.predict(df_train_scaled)
        val_pred = model.predict(df_val_scaled)

        train_conf = confusion_matrix(y_train, train_pred)
        val_conf = confusion_matrix(y_val, val_pred)

        result = pd.DataFrame({
            "gamma": [gamma],
            "max_depth": [max_depth],
            "learning_rate": [learning_rate],
            "n_estimators": [n_estimators],
            "min_child_weight": [min_child_weight],
            # Training
            "train_acc": [accuracy_score(y_train, train_pred)],
            "train_f1": [f1_score(y_train, train_pred)],
            "train_tp": [train_conf[1, 1]],
            "train_fp": [train_conf[0, 1]],
            "train_tn": [train_conf[0, 0]],
            "train_fn": [train_conf[1, 0]],
            "train_precision": [precision_score(y_train, train_pred)],
            "train_recall": [recall_score(y_train, train_pred)],
            "train_roc_auc": [roc_auc_score(y_train, train_pred)],
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

xgb_res.to_csv("./xgb.csv", index=False)
