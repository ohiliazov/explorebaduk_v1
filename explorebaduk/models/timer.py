import asyncio
import time
import itertools
from typing import SupportsFloat
from abc import ABCMeta, abstractmethod
from explorebaduk.constants import MOVE_DELAY
from explorebaduk.exceptions import OutOfTimeError


class Timer(metaclass=ABCMeta):
    def __init__(self, time_left: float, delay: int = MOVE_DELAY):
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
    async def process_time(self, time_used: float):
        pass


class NoTimeTimer(Timer):
    def __init__(self):
        time_left = float("+inf")
        super().__init__(time_left, 0)

    def process_time(self, time_used: float):
        return


class AbsoluteTimer(Timer):
    """
    Simple absolute timer
    """
    def __init__(self, main_time: int, delay: int = MOVE_DELAY):
        super().__init__(main_time, delay)

    def process_time(self, time_used: float):
        self.time_left -= time_used


class ByoyomiTimer(Timer):
    def __init__(self, main_time: int, overtime: int, periods: int, delay: int = MOVE_DELAY):
        time_left = main_time + overtime * periods
        super().__init__(time_left, delay)

        self.overtime = periods
        self.periods_left = periods

        # will only change once
        self.in_overtime = False

    def process_time(self, time_used: float):
        if self.in_overtime:
            periods_used, time_left = divmod(time_used, self.overtime)
            self.periods_left -= periods_used
            self.time_left = self.overtime * self.periods_left

        else:
            self.time_left -= time_used
            if self.time_left <= self.overtime * self.periods_left:
                self.in_overtime = True
                self.process_time(0)
