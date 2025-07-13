import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})
pred = np.array(
    [0.1, 0.13, -0.2, 0.1, 0.3, -0.5, -0.1, 0.4, 0.1, -0.3, -0.2, 0.05, -0.1, 0.2, 0.1, -0.4, 0.1, 0.15, -0.2, 0.1, 0.2,
     -0.1, 0.4])

cumsum = np.cumsum(pred)

max_v = np.max(cumsum)
min_v = np.min(cumsum)
print(max_v > min_v)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot([0, len(cumsum)], [0, 0], color="black")
ax1.plot(range(len(pred)), pred)
ax1.set_title("Predicted Logarithmic Returns")
ax2.plot([0, len(cumsum)], [0, 0], color="black")
ax2.plot(range(len(cumsum)), cumsum)
ax2.plot([0, len(cumsum)], [min_v, min_v], color="red", label="Minimum")
ax2.plot([0, len(cumsum)], [max_v, max_v], color="green", label="Maximum")
ax2.set_ylim((-0.55, 0.55))
ax1.set_ylim((-0.55, 0.55))

ax2.set_title("Cumulative Predicted Logarithmic Returns")

plt.show()
