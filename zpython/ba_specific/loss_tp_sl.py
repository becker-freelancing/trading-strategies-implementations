import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import numpy as np

fig, axs = plt.subplots(2, 2, figsize=(16, 9))

# Long High Vor Low
c1 = [0, -0.2, 0.2, 0.1, 0.3, -0.2, 0.4, -0.2, -0.4, 0.1, -0.2, -0.1, 0.1, -0.4, 0.3, -0.1, 0.2]
c1c = np.cumsum(c1)
axs[0, 0].plot(c1c)
axs[0, 0].plot([0, len(c1)], [np.min(c1c), np.min(c1c)], color="red")
axs[0, 0].plot([0, len(c1)], [np.max(c1c), np.max(c1c)], color="green")
axs[0, 0].fill_between(
    range(np.argmax(c1c) + 1),
    np.max(c1c),
    0,
    color="green", alpha=0.1
)
axs[0, 0].fill_between(
    range(np.argmax(c1c) + 1),
    np.min(c1c[:np.argmax(c1c)]),
    0,
    color="red", alpha=0.1
)
axs[0, 0].set_title("Long with Global High before Global Low")

# Long Low Vor High
c1 = [0, 0.2, -0.3, -0.3, -0.2, 0.1, 0.2, -0.1, 0.3, 0.2, -0.1, -0.2, 0.3, 0.4, -0.1, -0.2, 0.1]
c1c = np.cumsum(c1)
axs[0, 1].plot(c1c)
axs[0, 1].plot([0, len(c1)], [np.min(c1c), np.min(c1c)], color="red")
axs[0, 1].plot([0, len(c1)], [np.max(c1c), np.max(c1c)], color="green")
axs[0, 1].fill_between(
    range(np.argmax(c1c) + 1),
    np.max(c1c),
    0,
    color="green", alpha=0.1
)
axs[0, 1].fill_between(
    range(np.argmax(c1c) + 1),
    np.min(c1c[:np.argmax(c1c)]),
    0,
    color="red", alpha=0.1
)
axs[0, 1].set_title("Long with Global High after Global Low")

# Short High Vor Low
c1 = [0, -0.2, 0.2, 0.1, 0.3, -0.2, 0.4, -0.2, -0.4, 0.1, -0.2, -0.1, 0.1, -0.4, 0.3, -0.1, 0.2]
c1c = np.cumsum(c1)
axs[1, 0].plot(c1c)
axs[1, 0].plot([0, len(c1)], [np.min(c1c), np.min(c1c)], color="red")
axs[1, 0].plot([0, len(c1)], [np.max(c1c), np.max(c1c)], color="green")
axs[1, 0].fill_between(
    range(np.argmin(c1c) + 1),
    np.max(c1c),
    0,
    color="red", alpha=0.1
)
axs[1, 0].fill_between(
    range(np.argmin(c1c) + 1),
    np.min(c1c),
    0,
    color="green", alpha=0.1
)
axs[1, 0].set_title("Short with Global High before Global Low")

# Short Low Vor High
c1 = [0, 0.2, -0.3, -0.3, -0.2, 0.1, 0.2, -0.1, 0.3, 0.2, -0.1, -0.2, 0.3, 0.4, -0.1, -0.2, 0.1]
c1c = np.cumsum(c1)
axs[1, 1].plot(c1c)
axs[1, 1].plot([0, len(c1)], [np.min(c1c), np.min(c1c)], color="red")
axs[1, 1].plot([0, len(c1)], [np.max(c1c), np.max(c1c)], color="green")
axs[1, 1].fill_between(
    range(np.argmin(c1c) + 1),
    np.max(c1c[:np.argmin(c1c)]),
    0,
    color="red", alpha=0.1
)
axs[1, 1].fill_between(
    range(np.argmin(c1c) + 1),
    np.min(c1c),
    0,
    color="green", alpha=0.1
)
axs[1, 1].set_title("Short with Global High after Global Low")
plt.show()
