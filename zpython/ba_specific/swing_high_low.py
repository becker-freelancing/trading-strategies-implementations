import matplotlib

matplotlib.use("TkAgg")

from zpython.util.indicator_creator import create_indicators
from zpython.util.data_split import test_data

df = create_indicators(data_read_function=test_data)
print(df)
