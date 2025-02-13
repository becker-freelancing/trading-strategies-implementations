from enum import Enum


class Pair(Enum):
    PAXGUSD_1 = ("PAXGUSD_1", 1)
    PAXGUSD_5 = ("PAXGUSD_5", 5)
    EURUSD_1 = ("EURUSD_1", 1)
    EURUSD_5 = ("EURUSD_5", 5)

    def file_name(self):
        return self.value[0] + ".csv.zip"

    def name(self):
        return self.value[0]

    def minutes(self):
        return self.value[1]
