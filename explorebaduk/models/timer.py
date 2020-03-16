import time

from abc import ABCMeta, abstractmethod
from explorebaduk.constants import MOVE_DELAY, TimeSystem
from explorebaduk.exceptions import TimerError


class Timer(metaclass=ABCMeta):
    def __init__(self, remaining: float, delay: float = MOVE_DELAY, **kwargs):
        self._started_at = None

        self.remaining = remaining
        self.delay = delay

    def _reset(self):
        self._started_at = None

    @property
    def started(self):
        return self._started_at is not None

    @property
    def time_left(self):
        if self.started:
            return self.remaining + self._started_at - time.monotonic()
        return self.remaining

    def start(self):
        if self.started:
            raise TimerError("Already started")

        self._started_at = time.monotonic() + self.delay

        return self.remaining

    def stop(self):
        if not self.started:
            raise TimerError("Not started")

        time_used = time.monotonic() - self._started_at

        if time_used > 0:
            self.process_time(time_used)

            if self.remaining < 0:
                raise TimerError(f"Out of time")

        self._reset()

        return self.remaining

    @abstractmethod
    async def process_time(self, time_used: float) -> None:
        pass


class NoTimeTimer(Timer):
    """
    No time limit
    """

    def __init__(self, **kwargs):
        remaining = float("+inf")
        super().__init__(remaining, **kwargs)

    def process_time(self, time_used: float) -> None:
        return None


class AbsoluteTimer(Timer):
    """
    Each player is assigned a fixed amount of time for the whole game.
    If a player's main time expires, they generally lose the game.
    """

    def __init__(self, *, main_time: float, **kwargs):
        super().__init__(main_time, **kwargs)

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used


class ByoyomiTimer(Timer):
    """
    After the main time is depleted, a player has a certain number of periods.
    If a move is completed before the time expires, the time period resets and restarts the next turn.
    If a move is not completed within a time period, the time period will expire, and the next time period begins.
    """

    def __init__(self, *, main_time: float, overtime: float, periods: int, **kwargs):
        remaining = main_time + overtime * periods
        super().__init__(remaining, **kwargs)

        self.overtime = overtime
        self.periods = periods

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used

        periods_left = self.remaining // self.overtime

        if 0 <= periods_left < self.periods:
            self.remaining = self.overtime * (periods_left + 1)


class CanadianTimer(Timer):
    """
    After the main time is depleted, a player must make a certain number of moves within a certain period of time.
    """

    def __init__(
        self, *, main_time: float, overtime: float, stones: int, **kwargs,
    ):
        remaining = main_time + overtime
        super().__init__(remaining, **kwargs)

        self.overtime = overtime
        self.stones = self.stones_left = stones

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used

        if self.remaining < self.overtime:
            self.stones_left -= 1

            # next overtime period
            if self.stones_left == 0:
                self.remaining = self.overtime
                self.stones_left = self.stones

        else:
            self.stones_left = self.stones


class FischerTimer(Timer):
    """
    A specified amount of time is added to the players main time each move,
    unless the player's main time ran out before they completed their move.
    """

    def __init__(self, *, main_time: float, bonus: float, **kwargs):
        super().__init__(main_time, **kwargs)

        self.bonus = bonus

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used + self.bonus


TIMERS = {
    TimeSystem.NO_TIME: NoTimeTimer,
    TimeSystem.ABSOLUTE: AbsoluteTimer,
    TimeSystem.BYOYOMI: ByoyomiTimer,
    TimeSystem.CANADIAN: CanadianTimer,
    TimeSystem.FISCHER: FischerTimer,
}


def create_timer(time_system: TimeSystem, **time_settings) -> Timer:
    """
    Create timer for
    :param time_system:
    :param time_control_data: main_time, overtime,
    :return:
    """
    timer_class = TIMERS[time_system]

    return timer_class(**time_settings)
