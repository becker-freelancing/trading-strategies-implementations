from enum import Enum


class Pair(Enum):
    PAXGUSD_1 = ("PAXGUSD_1.csv.zip", 1)
    PAXGUSD_5 = ("PAXGUSD_5.csv.zip", 5)

    def file_name(self):
        return self.value[0]

    def minutes(self):
        return self.value[1]
