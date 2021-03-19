import time
from abc import ABCMeta, abstractmethod

# Delay before making a move
MOVE_DELAY = 1


class TimerError(Exception):
    pass


class Timer(metaclass=ABCMeta):
    def __init__(
        self,
        main_time: int = 0,
        overtime: int = 0,
        periods: int = 1,
        stones: int = 1,
        bonus: int = 0,
        time_left: float = None,
    ):
        self.main_time = main_time
        self.overtime = overtime
        self.periods = periods
        self.stones = stones
        self.bonus = bonus

        self.started_at = None
        self._time_left = time_left or self.initial_time_left()

    @property
    def started(self):
        return self.started_at is not None

    @property
    def time_used(self):
        return time.monotonic() - self.started_at if self.started else 0

    @property
    def time_left(self) -> float:
        return self._time_left - self.time_used

    def start(self) -> float:
        if self.started:
            raise TimerError("Already started")

        self.started_at = time.monotonic() + MOVE_DELAY

        return self.time_left

    def stop(self) -> float:
        if not self.started:
            raise TimerError("Not started")

        self._time_left -= max(0, self.time_used)
        if self._time_left <= 0:
            raise TimerError("Out of time")

        self.process_overtime()

        self.started_at = None

        return self.time_left

    @abstractmethod
    def initial_time_left(self):
        pass

    @abstractmethod
    def process_overtime(self) -> None:
        pass


class UnlimitedTimer(Timer):
    """
    No time limit
    """

    def initial_time_left(self):
        return 0

    def start(self):
        pass

    def stop(self):
        pass

    def process_overtime(self) -> None:
        pass


class AbsoluteTimer(Timer):
    """
    Each player is assigned a fixed amount of time for the whole game.
    If a player's main time expires, they generally lose the game.
    """

    def initial_time_left(self):
        return self.main_time

    def process_overtime(self) -> None:
        pass


class ByoyomiTimer(Timer):
    """
    After the main time is depleted, a player has a certain number of periods.
    If a move is completed before the time expires,
    the time period resets and restarts the next turn.
    If a move is not completed within a time period,
    the time period will expire, and the next time period begins.
    """

    def initial_time_left(self):
        return self.main_time + self.overtime * self.periods

    def process_overtime(self) -> None:
        periods_left = self._time_left // self.overtime

        if 0 <= periods_left < self.periods:
            self._time_left = self.overtime * (periods_left + 1)


class CanadianTimer(Timer):
    """
    After the main time is depleted, a player must make a certain number of moves
    within a certain period of time.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stones_left = self.stones

    def initial_time_left(self):
        return self.main_time + self.overtime * self.periods

    def process_overtime(self) -> None:
        if self._time_left < self.overtime:
            self.stones_left -= 1

            # next overtime period
            if self.stones_left == 0:
                self._time_left = self.overtime
                self.stones_left = self.stones

        else:
            self.stones_left = self.stones


class FischerTimer(Timer):
    """
    A specified amount of time is added to the players main time each move,
    unless the player's main time ran out before they completed their move.
    """

    def initial_time_left(self):
        return self.main_time

    def process_overtime(self) -> None:
        self._time_left += self.bonus
