import matplotlib

matplotlib.use("TkAgg")
from zpython.util import analysis_data
import matplotlib.pyplot as plt
import numpy as np
from zpython.util import split_on_gaps

thrsholds = np.arange(start=0.0002, stop=0.007, step=0.0002)

df = analysis_data()
durations = []
split = split_on_gaps(df, 1)
split = [df["closeBid"].values for df in split]

for th in thrsholds:
    val = []
    for df in split:
        for i in range(len(df)):
            current = df[i]
            target = current * (1 + th)
            t2 = current * (1 - th)
            found = np.where(df[i + 1:] >= target)[0]
            f2 = np.where(df[i + 1:] <= t2)[0]
            if len(found) > 0 and len(f2) > 0:
                val.append(min(found[0] + 1, f2[0] + 1))
            elif len(found) > 0:
                val.append(found[0] + 1)
            elif len(f2) > 0:
                val.append(f2[0] + 1)
            else:
                continue

    durations.append(val)

fig, ax = plt.subplots()

ax.boxplot(durations, tick_labels=thrsholds)
plt.show()
