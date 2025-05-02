import warnings

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta
from scipy.stats import linregress
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

from IPython.display import clear_output

clear_output()

df = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_5.csv.zip", compression="zip")
df = df.iloc[len(df) - 5000:]
df.rename(columns={
    "openBid": "Open",
    "highBid": "High",
    "lowBid": "Low",
    "closeBid": "Close"
}, inplace=True)

print(df.head())

# Get new features
df['RSI'] = ta.rsi(df["Close"])
df['ATR'] = ta.atr(df["High"], df["Low"], df["Close"], length=20)
df['Average'] = ta.midprice(df["High"], df["Low"], length=1)
df['MA40'] = ta.sma(df["Close"], length=40)
df['MA80'] = ta.sma(df["Close"], length=80)
df['MA160'] = ta.sma(df["Close"], length=160)

# Plot open price and moving averages
plt.figure(figsize=(14, 4))
plt.plot(df.index, df["Open"])
plt.plot(df.index, df.MA40, ls=':')
plt.plot(df.index, df.MA80, ls=':')
plt.plot(df.index, df.MA160, ls=':')
plt.legend(['Open', 'MA40', 'MA80', 'MA160'])
plt.title('[EUR/USD] Open Price and Moving Averages')
plt.xlabel('Date')
plt.ylabel('EUR/USD')
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.show()

# Plot RSI
plt.figure(figsize=(14, 4))
plt.plot(df.index, df.RSI, lw=1, color='gray')
plt.axhline(70, ls='--', color='red')
plt.axhline(30, ls='--', color='red')
plt.legend(['RSI'])
plt.title('Relative Strength Index (RSI)')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.show()


def get_slope(array):
    y = np.array(array)
    x = np.arange(len(y))
    slope = linregress(x, y)[0]
    return slope


# Get slope features
back_rolling_n = 6
df['slopeMA40'] = df['MA40'].rolling(window=back_rolling_n).apply(get_slope, raw=True)
df['slopeMA80'] = df['MA80'].rolling(window=back_rolling_n).apply(get_slope, raw=True)
df['slopeMA160'] = df['MA160'].rolling(window=back_rolling_n).apply(get_slope, raw=True)
df['AverageSlope'] = df['Average'].rolling(window=back_rolling_n).apply(get_slope, raw=True)
df['RSISlope'] = df['RSI'].rolling(window=back_rolling_n).apply(get_slope, raw=True)

# Plot the moving average slopes
plt.figure(figsize=(14, 4))
plt.plot(df.index, df.slopeMA40, lw=1, ls=':', color='orange')
plt.plot(df.index, df.slopeMA80, lw=1, ls=':', color='green')
plt.plot(df.index, df.slopeMA160, lw=1, ls=':', color='red')
plt.axhline(0, ls='-.', color='black')
plt.legend(['slopeMA40', 'slopeMA80', 'slopeMA160'])
plt.gca().xaxis.set_major_locator(mdates.YearLocator())
plt.title('Moving Average Slopes')
plt.xlabel('Year')
plt.ylabel('Slope')
plt.show()

TP_pipdiff = 0.0001
TPSLRatio = 3
SL_pipdiff = TP_pipdiff / TPSLRatio


def get_target(barsupfront, df):
    length = len(df)
    high = list(df['High'])
    low = list(df['Low'])
    close = list(df['Close'])
    open = list(df['Open'])
    trendcat = [None] * length

    for line in range(0, length - barsupfront - 2):
        valueOpenLow = 0
        valueOpenHigh = 0
        for i in range(0, barsupfront + 2):
            openLowDiff = open[line + 1] - low[line + i]
            openHighDiff = open[line + 1] - high[line + i]
            valueOpenLow = max(openLowDiff, valueOpenLow)
            valueOpenHigh = min(openHighDiff, valueOpenHigh)

            if ((valueOpenLow >= TP_pipdiff) and (-valueOpenHigh <= SL_pipdiff)):
                trendcat[line] = 1  # Downtrend
                break
            elif ((valueOpenLow <= SL_pipdiff) and (-valueOpenHigh >= TP_pipdiff)):
                trendcat[line] = 2  # Uptrend
                break
            else:
                trendcat[line] = 0  # No clear trend

    return trendcat


df['target'] = get_target(1000, df)

fig = plt.figure(figsize=(20, 8))
ax = fig.gca()
df_model = df[['ATR', 'RSI', 'Average', 'MA40', 'MA80', 'MA160',
               'slopeMA40', 'slopeMA80', 'slopeMA160',
               'AverageSlope', 'RSISlope', 'target']]
df_model.hist(ax=ax)
plt.suptitle("Histograms for the different features (and the target)")
plt.tight_layout()
plt.show()

plt.figure(figsize=(6, 3))
df_up = df.RSI[df.target == 2]
df_down = df.RSI[df.target == 1]
df_unclear = df.RSI[df.target == 0]
plt.hist(df_unclear, bins=50, alpha=0.5, label='unclear')
plt.hist(df_down, bins=50, alpha=0.5, label='down')
plt.hist(df_up, bins=50, alpha=0.5, label='up')
plt.title('Distribution of RSI within Target Classes')
plt.xlabel('RSI')
plt.ylabel('Amount')
plt.legend()
plt.show()

df_model = df_model.dropna()
features = ['ATR', 'RSI', 'Average', 'MA40', 'MA80', 'MA160',
            'slopeMA40', 'slopeMA80', 'slopeMA160', 'AverageSlope', 'RSISlope']
X = df_model[features]
y = df_model['target']
X.head()

split_index = int(0.8 * len(df_model))
X_train, X_valid = X[:split_index], X[split_index:]
y_train, y_valid = y[:split_index], y[split_index:]

# Fitting and predictions
knn_params = {'n_neighbors': 200,
              'weights': 'uniform',
              'algorithm': 'ball_tree',
              'leaf_size': 30,
              'p': 1,
              'metric': 'minkowski',
              'metric_params': None,
              'n_jobs': 1}

model = KNeighborsClassifier(**knn_params)
model.fit(X_train, y_train)
y_pred_train = model.predict(X_train)
y_pred_valid = model.predict(X_valid)
gambler_pred = np.random.choice([0, 1, 2], len(y_pred_valid))  # Was wäre, wenn ich random vorhersage

# Evaluating
train_accuracy = accuracy_score(y_train, y_pred_train)
valid_accuracy = accuracy_score(y_valid, y_pred_valid)
gambler_accuracy = accuracy_score(y_valid, gambler_pred)
base_accuracy = max(df_model.target.value_counts().sort_index() / len(df_model))
print("===================== KNN")
print(f"Train accuracy:   {train_accuracy * 100 :.2f}%")
print(f"Valid accuracy:   {valid_accuracy * 100 :.2f}%")
print(f"Gambler accuracy: {gambler_accuracy * 100 :.2f}%")
print("\nRepartition of the classes:")
print(df_model.target.value_counts().sort_index() / len(df_model))
print(f"\n=== Accuracy improvement: {(valid_accuracy - base_accuracy) * 100 :.2f}% ===")

model = XGBClassifier()
model.fit(X_train, y_train)
y_pred_train = model.predict(X_train)
y_pred_valid = model.predict(X_valid)
gambler_pred = np.random.choice([0, 1, 2], len(y_pred_valid))  # Was wäre, wenn ich random vorhersage

# Evaluating
train_accuracy = accuracy_score(y_train, y_pred_train)
valid_accuracy = accuracy_score(y_valid, y_pred_valid)
gambler_accuracy = accuracy_score(y_valid, gambler_pred)
base_accuracy = max(df_model.target.value_counts().sort_index() / len(df_model))
print("===================== XGBoost")
print(f"Train accuracy:   {train_accuracy * 100 :.2f}%")
print(f"Valid accuracy:   {valid_accuracy * 100 :.2f}%")
print(f"Gambler accuracy: {gambler_accuracy * 100 :.2f}%")
print("\nRepartition of the classes:")
print(df_model.target.value_counts().sort_index() / len(df_model))
print(f"\n=== Accuracy improvement: {(valid_accuracy - base_accuracy) * 100 :.2f}% ===")

# Compute cross-validation
n_splits_range = range(2, 12)
all_scores = [];
all_n_splits = [];
mean_scores = []
for n_splits in n_splits_range:
    tscv = TimeSeriesSplit(n_splits=n_splits)
    split_scores = []
    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        model = KNeighborsClassifier(**knn_params)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        all_n_splits.append(n_splits)
        all_scores.append(score)
        split_scores.append(score)
    mean_scores.append(np.mean(split_scores))

# Get data for first and last folds
first_fold_indices = [0];
last_fold_indices = [1]
for i in range(2, 11):
    first_fold_indices.append(first_fold_indices[-1] + i)
for i in range(3, 12):
    last_fold_indices.append(last_fold_indices[-1] + i)
first_fold_scores = [all_scores[i] for i in first_fold_indices]
last_fold_scores = [all_scores[i] for i in last_fold_indices]

# Display
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(n_splits_range, mean_scores)
plt.axhline(base_accuracy, color='black', ls='--')
plt.axhline(np.mean(mean_scores), color='red', ls='--')
plt.xticks(n_splits_range)
plt.title("Mean scores curve")
plt.xlabel("Number of splits")
plt.ylabel("Accuracy")
plt.legend(["Mean scores curve", "Base accuracy", "Mean of means"])
plt.subplot(1, 2, 2)
plt.scatter(all_n_splits, all_scores, marker='+', color='green')
plt.plot(n_splits_range, first_fold_scores, lw=1, ls=':', color='black')
plt.plot(n_splits_range, last_fold_scores, lw=1, ls=':', color='gray')
plt.plot(n_splits_range, mean_scores)
plt.axhline(base_accuracy, color='black', ls='--')
plt.axhline(np.mean(mean_scores), color='red', ls='--')
plt.xticks(n_splits_range)
plt.title("All individual scores")
plt.xlabel("Number of splits")
plt.legend(["Individual scores", "First splits", "Last splits"])
plt.show()

acc_improvement = (np.mean(mean_scores) - base_accuracy) * 100
print(f"=== Accuracy improvement: {acc_improvement:.2f}% ===")
