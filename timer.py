"""
Provides a Timer class to measure execution time in milliseconds.
The entire code was taken from lecture 8 (available at:
https://github.com/tj314/ppds-seminars/blob/ppds2024/lecture8/timer.py).
"""
from time import perf_counter_ns


TIMER = perf_counter_ns


class Timer:
    def __init__(self):
        self.start = TIMER()
        self.lap = self.start

    def start(self):
        self.lap = TIMER()

    def reset(self):
        self.lap = TIMER()

    def lap_ms(self):
        old_lap = self.lap
        lap = TIMER()
        return (lap - old_lap) / 1_000_000
