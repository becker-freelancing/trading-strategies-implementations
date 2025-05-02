from enum import Enum


class Pair(Enum):
    PAXGUSD_1 = ("PAXGUSD_1", 1)
    PAXGUSD_5 = ("PAXGUSD_5", 5)
    EURUSD_1 = ("EURUSD_1", 1)
    EURUSD_1_2024 = ("EURUSD_1_2024", 1)
    EURUSD_5_2024 = ("EURUSD_5_2024", 5)
    EURUSD_15_2024 = ("EURUSD_15_2024", 15)
    EURUSD_30_2024 = ("EURUSD_30_2024", 30)
    EURUSD_60_2024 = ("EURUSD_60_2024", 60)
    EURUSD_1440 = ("EURUSD_1440", 1440)
    EURUSD_5 = ("EURUSD_5", 5)

    def file_name(self):
        return self.value[0] + ".csv.zip"

    def name(self):
        return self.value[0]

    def minutes(self):
        return self.value[1]
