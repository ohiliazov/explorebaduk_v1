from enum import Enum
from functools import total_ordering


class TimeSystem(str, Enum):
    UNLIMITED = "unlimited"
    ABSOLUTE = "absolute"
    BYOYOMI = "byo-yomi"
    CANADIAN = "canadian"
    FISCHER = "fischer"


class GameCategory(str, Enum):
    REAL_TIME = "real-time"
    CORRESPONDENCE = "correspondence"


class RuleSet(str, Enum):
    JAPANESE = "japanese"
    CHINESE = "chinese"


@total_ordering
class Rank(str, Enum):
    PRO_9 = "9p"
    PRO_8 = "8p"
    PRO_7 = "7p"
    PRO_6 = "6p"
    PRO_5 = "5p"
    PRO_4 = "4p"
    PRO_3 = "3p"
    PRO_2 = "2p"
    PRO_1 = "1p"

    DAN_7 = "7d"
    DAN_6 = "6d"
    DAN_5 = "5d"
    DAN_4 = "4d"
    DAN_3 = "3d"
    DAN_2 = "2d"
    DAN_1 = "1d"

    KYU_1 = "1k"
    KYU_2 = "2k"
    KYU_3 = "3k"
    KYU_4 = "4k"
    KYU_5 = "5k"
    KYU_6 = "6k"
    KYU_7 = "7k"
    KYU_8 = "8k"
    KYU_9 = "9k"
    KYU_10 = "10k"

    KYU_11 = "11k"
    KYU_12 = "12k"
    KYU_13 = "13k"
    KYU_14 = "14k"
    KYU_15 = "15k"
    KYU_16 = "16k"
    KYU_17 = "17k"
    KYU_18 = "18k"
    KYU_19 = "19k"
    KYU_20 = "20k"

    KYU_21 = "21k"
    KYU_22 = "22k"
    KYU_23 = "23k"
    KYU_24 = "24k"
    KYU_25 = "25k"
    KYU_26 = "26k"
    KYU_27 = "27k"
    KYU_28 = "28k"
    KYU_29 = "29k"
    KYU_30 = "30k"

    def __eq__(self, other: "Rank"):
        return self.value == other.value

    def __gt__(self, other: "Rank"):
        val, rank = self.value[:-1], self.value[-1]
        other_val, other_rank = other.value[:-1], other.value[-1]

        if rank != other_rank:
            return "kdp".index(rank) > "kdp".index(other_rank)

        return val < other_val if rank == "k" else val > other_val
