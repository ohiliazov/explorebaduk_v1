import time
from abc import ABCMeta, abstractmethod

from explorebaduk.database import TimerModel, db
from explorebaduk.constants import MOVE_DELAY, TimeSystem
from explorebaduk.exceptions import TimerError


class TimerBase(metaclass=ABCMeta):
    def __init__(
        self,
        game_id: int,
        player_id: int,
        *,
        main_time: int = 0,
        overtime: int = 0,
        periods: int = 1,
        stones: int = 1,
        bonus: int = 0,
    ):
        self._game_id = game_id
        self._player_id = player_id

        self._started_at = None
        self._time_left = None

        self.main_time = main_time
        self.overtime = overtime
        self.periods = periods
        self.stones = stones
        self.bonus = bonus
        self.delay = MOVE_DELAY

    def save_to_db(self):
        pass

    def _reset(self):
        self._started_at = None

    @property
    def started(self):
        return self._started_at is not None

    @property
    def time_left(self):
        if self.started:
            return self._time_left + self._started_at - time.monotonic()
        return self._time_left

    def start(self):
        if self.started:
            raise TimerError("Already started")

        self._started_at = time.monotonic() + self.delay

        return self._time_left

    def stop(self):
        if not self.started:
            raise TimerError("Not started")

        time_used = time.monotonic() - self._started_at

        if time_used > 0:
            self.process_time(time_used)

            if self._time_left < 0:
                raise TimerError(f"Out of time")

        self._reset()

        return self._time_left

    @abstractmethod
    def process_time(self, time_used: float) -> None:
        pass


class NoTimeTimerBase(TimerBase):
    """
    No time limit
    """

    def start(self):
        return 0

    def stop(self):
        return 0

    def process_time(self, time_used: float) -> None:
        pass


class AbsoluteTimerBase(TimerBase):
    """
    Each player is assigned a fixed amount of time for the whole game.
    If a player's main time expires, they generally lose the game.
    """

    def __init__(self, *, main_time: int, **kwargs):
        super().__init__(main_time=main_time)
        self.remaining = main_time

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used


class ByoyomiTimerBase(TimerBase):
    """
    After the main time is depleted, a player has a certain number of periods.
    If a move is completed before the time expires, the time period resets and restarts the next turn.
    If a move is not completed within a time period, the time period will expire, and the next time period begins.
    """

    def __init__(self, *, main_time: int, overtime: int, periods: int, **kwargs):
        super().__init__(main_time=main_time, overtime=overtime, periods=periods)
        self.remaining = main_time + overtime * periods

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used

        periods_left = self.remaining // self.overtime

        if 0 <= periods_left < self.periods:
            self.remaining = self.overtime * (periods_left + 1)


class CanadianTimerBase(TimerBase):
    """
    After the main time is depleted, a player must make a certain number of moves within a certain period of time.
    """

    def __init__(self, *, main_time: int, overtime: int, stones: int, **kwargs):
        super().__init__(main_time=main_time, overtime=overtime, stones=stones)
        self.remaining = main_time + overtime
        self.stones_left = stones

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


class FischerTimerBase(TimerBase):
    """
    A specified amount of time is added to the players main time each move,
    unless the player's main time ran out before they completed their move.
    """

    def __init__(self, *, main_time: int, bonus: int, **kwargs):
        super().__init__(main_time=main_time, bonus=bonus)
        self.remaining = main_time

    def process_time(self, time_used: float) -> None:
        self.remaining -= time_used + self.bonus


TIMERS = {
    TimeSystem.NO_TIME: NoTimeTimerBase,
    TimeSystem.ABSOLUTE: AbsoluteTimerBase,
    TimeSystem.BYOYOMI: ByoyomiTimerBase,
    TimeSystem.CANADIAN: CanadianTimerBase,
    TimeSystem.FISCHER: FischerTimerBase,
}


def create_timer(time_system: TimeSystem, **time_settings) -> TimerBase:
    """
    Create timer
    :param time_system: type of time control system
    :param time_settings: main_time, overtime, periods, stones, bonus
    :return: timer
    """
    return TIMERS[time_system](**time_settings)
