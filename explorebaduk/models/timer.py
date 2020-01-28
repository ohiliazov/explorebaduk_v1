import asyncio
import time

from abc import ABCMeta, abstractmethod
from explorebaduk.constants import MOVE_DELAY, TimeSystem
from explorebaduk.exceptions import OutOfTimeError


class Timer(metaclass=ABCMeta):
    def __init__(self, time_left: float, delay: float = MOVE_DELAY):
        self._started_at = None

        self.time_left = time_left
        self.delay = delay

    def _reset(self):
        self._started_at = None

    def start(self):
        self._started_at = time.monotonic() + self.delay

    def stop(self):
        time_used = time.monotonic() - self._started_at

        if time_used > 0:
            self.process_time(time_used)

            if self.time_left < 0:
                raise OutOfTimeError(f"Time left: {self.time_left} used: {time_used}")

        self._reset()

    @abstractmethod
    async def process_time(self, time_used: float) -> None:
        pass


class NoTimeTimer(Timer):
    def __init__(self):
        time_left = float("+inf")
        super().__init__(time_left, 0)

    def process_time(self, time_used: float) -> None:
        return None


class AbsoluteTimer(Timer):
    """
    Simple absolute timer
    """
    def __init__(self, main_time: float, delay: float = MOVE_DELAY):
        super().__init__(main_time, delay)

    def process_time(self, time_used: float) -> None:
        self.time_left -= time_used


class ByoyomiTimer(Timer):
    def __init__(self, main_time: float, overtime: float, periods: int, delay: float = MOVE_DELAY):
        time_left = main_time + overtime * periods
        super().__init__(time_left, delay)

        self.overtime = overtime
        self.periods = periods

    def process_time(self, time_used: float) -> None:
        self.time_left -= time_used

        periods_left = self.time_left // self.overtime

        if 0 <= periods_left < self.periods:
            self.time_left = self.overtime * (periods_left + 1)


class CanadianTimer(Timer):
    def __init__(self, main_time: float, overtime: float, stones: int, delay: float = MOVE_DELAY):
        time_left = main_time + overtime
        super().__init__(time_left, delay)

        self.overtime = overtime
        self.stones = self.stones_left = stones

    def process_time(self, time_used: float) -> None:
        self.time_left -= time_used

        if self.time_left < self.overtime:
            self.stones_left -= 1

            # next overtime period
            if self.stones_left == 0:
                self.time_left = self.overtime
                self.stones_left = self.stones

        else:
            self.stones_left = self.stones


class FischerTimer(Timer):
    def __init__(self, main_time: float, bonus: float, delay: float = MOVE_DELAY):
        super().__init__(main_time, delay)

        self.bonus = bonus

    def process_time(self, time_used: float) -> None:
        self.time_left -= time_used + self.bonus


def create_timer(time_system: TimeSystem, data: dict) -> Timer:
    if time_system is TimeSystem.NO_TIME:
        return NoTimeTimer()

    if time_system is TimeSystem.ABSOLUTE:
        return AbsoluteTimer(data['main_time'])

    if time_system is TimeSystem.BYOYOMI:
        return ByoyomiTimer(data['main_time'], data['overtime'], data['periods'])

    if time_system is TimeSystem.CANADIAN:
        return ByoyomiTimer(data['main_time'], data['overtime'], data['stones'])

    if time_system is TimeSystem.FISCHER:
        return FischerTimer(data['main_time'], data['bonus'])

    raise NotImplementedError
