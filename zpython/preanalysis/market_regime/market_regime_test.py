import numpy as np
import ta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from zpython.util import analysis_data

print("Read data")
df = analysis_data()
print("Create indicators")
df["rsi"] = ta.momentum.RSIIndicator(df["closeBid"]).rsi()
df["macd"] = ta.trend.MACD(df["closeBid"]).macd()
df["bollinger_width"] = ta.volatility.BollingerBands(df["closeBid"]).bollinger_wband()
df["atr"] = ta.volatility.AverageTrueRange(df["highBid"], df["lowBid"], df["closeBid"]).average_true_range()
df["roc"] = ta.momentum.ROCIndicator(df["closeBid"]).roc()


def label_market_regime(close_series, window=60, threshold=0.01):
    """Klassifiziert in Trend-Aufwärts, Trend-Abwärts, oder Seitwärts"""
    returns = close_series.pct_change(periods=window)
    direction = np.where(returns > threshold, 1, np.where(returns < -threshold, -1, 0))
    return direction


print("Create labels")
df["regime"] = label_market_regime(df["closeBid"])
features = ["rsi", "macd", "bollinger_width", "atr", "roc"]
df = df.dropna()
X = df[features]
y = df["regime"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)

from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment


# === Label Mapping für KMeans ===
def map_clusters_to_labels(true_labels, cluster_labels):
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(true_labels, cluster_labels)
    row_ind, col_ind = linear_sum_assignment(-cm)
    mapping = dict(zip(col_ind, row_ind))
    mapped = np.vectorize(mapping.get)(cluster_labels)
    return mapped


# === Modell 1: Random Forest ===
print("Random forest")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_preds = rf.predict(X_test)
rf_acc = accuracy_score(y_test, rf_preds)
rf_cm = confusion_matrix(y_test, rf_preds)

# === Modell 2: KMeans ===
print("KMeans")
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_train)
kmeans_preds = kmeans.predict(X_test)
mapped_kmeans_preds = map_clusters_to_labels(y_test, kmeans_preds)
kmeans_acc = accuracy_score(y_test, mapped_kmeans_preds)
kmeans_cm = confusion_matrix(y_test, mapped_kmeans_preds)

# === Modell 3: SVM ===
print("SVM")
svm = SVC()
svm.fit(X_train, y_train)
svm_preds = svm.predict(X_test)
svm_acc = accuracy_score(y_test, svm_preds)
svm_cm = confusion_matrix(y_test, svm_preds)

# === Modell 4: XGBoost ===
try:
    print("XGBoost")
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
    xgb.fit(X_train, y_train + 1)
    xgb_preds = xgb.predict(X_test)
    xgb_acc = accuracy_score(y_test + 1, xgb_preds)
    xgb_cm = confusion_matrix(y_test + 1, xgb_preds)
except Exception as e:
    print(e)

# === Modell 5: KNN ===
print("KNN")
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
knn_preds = knn.predict(X_test)
knn_acc = accuracy_score(y_test, knn_preds)
knn_cm = confusion_matrix(y_test, knn_preds)

# === Ergebnisvergleich & Confusion Matrices ===
print(f"\n\nRandom Forest Accuracy: {rf_acc:.4f}")
print(f"Confusion Matrix (Random Forest): \n{rf_cm}")

print(f"\n\nKMeans Accuracy (mapped): {kmeans_acc:.4f}")
print(f"Confusion Matrix (KMeans): \n{kmeans_cm}")

print(f"\n\nSVM Accuracy: {svm_acc:.4f}")
print(f"Confusion Matrix (SVM): \n{svm_cm}")

print(f"\n\nKNN Accuracy: {knn_acc:.4f}")
print(f"Confusion Matrix (KNN): \n{knn_cm}")

print(f"\n\nXGBoost Accuracy: {xgb_acc:.4f}")
print(f"Confusion Matrix (XGBoost): \n{xgb_cm}")
