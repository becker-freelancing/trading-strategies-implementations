import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from zpython.util.indicator_creator import create_indicators
from pandas.plotting import scatter_matrix

df, det = create_indicators()

df = df.iloc[-20000:]

scatter_matrix(df, alpha=0.8, figsize=(8, 8), diagonal='hist')
plt.show()
