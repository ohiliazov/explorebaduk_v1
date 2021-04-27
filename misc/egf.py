"""
EGF Official Rating System (since 2021)

https://www.europeangodatabase.eu/EGD/EGF_rating_system.php
"""

from decimal import Decimal


def con(r: Decimal) -> Decimal:
    """Rating volatility factor"""
    return ((3300 - r) / 200) ** Decimal("1.6")


def beta(r: Decimal) -> Decimal:
    """Mapping function for EGD ratings"""
    return -7 * (3300 - r).ln()


def se(r1: Decimal, r2: Decimal) -> Decimal:
    """Expected result computed by Bradley-Terry formula"""
    return 1 / (1 + (beta(r2) - beta(r1)).exp())


def bonus(r: Decimal) -> Decimal:
    """Term to counter rating deflation"""
    return (((2300 - r) / 80).exp() + 1).ln() / 5


def calculate(r1: Decimal, r2: Decimal, sa: Decimal) -> Decimal:
    """Calculate new rating of the player

    :param r1: EGD rating of the player
    :param r2: EGD rating of the opponent
    :param sa: actual game result
    """
    return r1 + con(r1) * (sa - se(r1, r2)) + bonus(r1)
