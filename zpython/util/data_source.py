from enum import Enum

from zpython.util.pair import Pair
from zpython.util.path_util import from_relative_path


class DataSource(str, Enum):
    KRAKEN_SPREAD = "KRAKEN_SPREAD"
    KRAKEN = "KRAKEN"
    IG = "IG"
    HIST_DATA = "HIST_DATA"

    def file_path(self, pair: Pair):
        if self == DataSource.IG:
            return from_relative_path(f"data-ig/{pair.file_name()}")
        if self == DataSource.KRAKEN_SPREAD:
            return from_relative_path(f"data-kraken-spread/{pair.file_name()}")
        if self == DataSource.KRAKEN:
            return from_relative_path(f"data-kraken/{pair.file_name()}")
        if self == DataSource.HIST_DATA:
            return from_relative_path(f"data-histdata/{pair.file_name()}")
