import matplotlib.pyplot as plt
import numpy as np

for _ in range(50):
    start = 5000
    results = []
    for i in range(8000):
        if start < 0:
            break
        win = 1 if np.random.random() < 0.35 else -1
        sl = start * 0.01
        tp = 2 * sl
        start = start + tp if win == 1 else start - sl
        start = start - 1
        results.append(start)

    plt.plot(results)
plt.show()
