import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

price = [1000, 1100, 1050, 1300, 1200]
xs = [1, 2, 3, 5, 6]

plt.plot(xs, price, color="black", label="Closing Price")
plt.plot([1, 2, 3.4, 5, 6], [940, 1040, 1040, 1240, 1240], color="red", label="Trailing Stop Level")
plt.fill_between([1, 2], [940, 1040], [1000, 1100], color="lightgreen")
plt.fill_between([2, 3, 3.4], [1040, 1040, 1040], [1100, 1050, 1100], color="lightcoral")
plt.fill_between([3.4, 5], [1040, 1240], [1100, 1300], color="lightgreen")
plt.fill_between([5, 5.6], [1240, 1240], [1300, 1240], color="lightcoral")
plt.scatter(1, 1000, label="Position Opened")
plt.scatter(1, 940, label="Initial Stop Level")
plt.scatter([5.6], [1240], label="Stop Loss Reached")
plt.title("Trailing Stop Example")
plt.xlabel("Time")
plt.ylabel("Price")
plt.grid()
plt.legend()
plt.show()
