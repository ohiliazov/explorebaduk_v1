import time


class Timer:
    def __init__(self):
        self.clock = None

    def reset_clock(self):
        self.clock = None

    def start_clock(self):
        self.clock = time.time()

    def stop_clock(self):
        time_used = time.time() - self.clock
        self.reset_clock()
        return time_used


class MainTime(Timer):
    def __init__(self, main_time: int):
        super().__init__()

        self._time_left = main_time

    @property
    def time_left(self):
        return max(0, self._time_left)

    def stop(self):
        time_used = self.stop_clock()
        self._time_left -= time_used

        if not self.time_left:
            raise Exception("Ran out of time")


class Byoyomi(Timer):
    def __init__(self, per_move: int, periods):
        super().__init__()

        self.per_move = per_move
        self.periods = periods

    @property
    def time_left(self):
        return max(0, self.per_move * self.periods)

    def stop(self):
        time_used = self.stop_clock()
        periods_used, time_left = divmod(time_used, self.per_move)
        self.periods -= periods_used

        if not self.time_left:
            raise Exception("Ran out of time")
