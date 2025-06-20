from zpython.util.data_split import test_data
from zpython.util.indicator_creator import create_indicators

df = create_indicators(test_data)

print(df)
