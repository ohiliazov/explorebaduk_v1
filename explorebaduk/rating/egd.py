import math
from decimal import Decimal

ALLOWED_RESULTS = {0, 0.5, 1}
EPSILON = Decimal("0.016")


def a_factor(rating: Decimal) -> Decimal:
    return Decimal(205 - rating / 20) if rating < 2700 else 70


def k_factor(rating: Decimal) -> Decimal:
    if rating < 200:
        k = 122 - rating * Decimal("0.06")
    elif rating < 1300:
        k = 120 - rating * Decimal("0.05")
    elif rating < 2000:
        k = 107 - rating * Decimal("0.04")
    elif rating < 2400:
        k = 87 - rating * Decimal("0.03")
    elif rating < 2600:
        k = 63 - rating * Decimal("0.02")
    elif rating < 2700:
        k = 37 - rating * Decimal("0.01")
    else:
        k = Decimal("10")

    return k


def calc_win_exp(r1: Decimal, r2: Decimal) -> Decimal:
    a = a_factor(min(r1, r2))
    d = Decimal(abs(r1 - r2))

    win_prob = 1 / Decimal(math.exp(d / a) + 1)

    if r1 >= r2:
        win_prob = 1 - win_prob

    return win_prob - (EPSILON / 2)


def egd_rating(r1: Decimal, r2: Decimal, result=1) -> Decimal:
    if result not in ALLOWED_RESULTS:
        return r1

    win_exp = calc_win_exp(r1, r2)
    growth = k_factor(r1) * (result - win_exp)

    return max(r1 + growth, Decimal("100"))
