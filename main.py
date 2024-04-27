"""
This module solves the sixth task. The solution was
inspired by the codes from lecture 11
(available at:
https://github.com/tj314/ppds-seminars/tree/ppds2024/lecture11)
and seminar 11
(available at:
https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar11).
"""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

from typing import Callable


def consumer(func: Callable) -> Callable:
    """Call `next` automatically on a generator."""

    def wrapper(*args, **kw):
        it = func(*args, **kw)
        next(it)
        return it

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


class Scheduler:
    """Class to manage and execute coroutines."""
    def __init__(self):
        """Initialize the Scheduler with an empty list of jobs."""
        self._jobs = []

    def add_job(self, it):
        """Add a coroutine job to the scheduler.

        :param it: The coroutine iterator to add.
        """
        self._jobs.append(it)

    def start(self, data):
        """Start executing the coroutines with provided data.

        :param data: The data to send to the coroutines.
        """
        counter = 0
        finished_coroutine_counter = 0
        while self._jobs:
            for i, job in enumerate(self._jobs):
                try:
                    if counter < len(data):
                        job.send(data[counter])
                        counter += 1
                    else:
                        job.close()
                        job.send(None)
                except StopIteration:
                    finished_coroutine_counter += 1
                    print(f"Job {i + 1} finished.")
                    if finished_coroutine_counter == 3:
                        print(f"All jobs finished.")
                        self._jobs.clear()


@consumer
def coroutine1():
    """Coroutine that converts data to uppercase."""
    try:
        while True:
            data = yield
            print("Coroutine 1:", data.upper())
    except GeneratorExit:
        print("Stops coroutine 1")


@consumer
def coroutine2():
    """Coroutine that alternates uppercase and lowercase characters."""
    try:
        while True:
            data = yield
            new = ""
            for index, letter in enumerate(data):
                if index % 2 == 0:
                    new += letter.upper()
                else:
                    new += letter.lower()
            print("Coroutine 2:", new)
    except GeneratorExit:
        print("Stops coroutine 2")


@consumer
def coroutine3():
    """A coroutine that replaces spaces with underscores and
    adds an underscore before and after a string."""
    try:
        while True:
            data = yield
            new = "_" + data.replace(" ", "_") + "_"
            print("Coroutine 3:", new)
    except GeneratorExit:
        print("Stops coroutine 3")


def main():
    """Main function to initialize and start the scheduler
    with coroutines."""
    scheduler = Scheduler()
    it1 = coroutine1()
    scheduler.add_job(it1)
    it2 = coroutine2()
    scheduler.add_job(it2)
    it3 = coroutine3()
    scheduler.add_job(it3)
    data = ["Ide", "piesen", "dokola", "okolo", "stola", "-la -la ...",
            "tralala"]
    scheduler.start(data)


if __name__ == "__main__":
    main()
