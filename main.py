"""This module solves the third task."""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

from time import sleep
from fei.ppds import Thread, Semaphore, print, Mutex

C = 5
N = 10


class SimpleBarrier:
    """
    A simple barrier implementation.
    The implementation of this class is inspired by the example
    from the second lecture, which is available at :
    https://elearn.elf.stuba.sk/moodle/pluginfile.php/77169/mod_resource/content/2/2024-02.mutex%20multiplex%20randezvouse%20bariera.pdf.
    """
    def __init__(self):
        """Initializes the barrier."""
        self.mutex = Mutex()
        self.barrier = Semaphore(0)
        self.barrierCount = 0

    def wait(self, i, shared, in_out):
        """
        Waits for all threads to reach the barrier and then proceeds.

        :param i: The identifier of the passenger/thread
        :param shared: Shared resources among threads
        :param in_out: Denotes whether the passenger is boarding (1) or getting off the train (0)
        """
        self.mutex.lock()
        self.barrierCount += 1
        if in_out == 1:
            print(f"The passenger {i} boarded the train. Number of passengers on the train: {self.barrierCount}.")
        else:
            print(f"The passenger {i} is ready to get off the train. Number of ready passengers: {self.barrierCount}.")
        if self.barrierCount == C:
            if in_out == 1:
                print(f"All passengers are on the train waiting to depart.")
                shared.boarded.signal()
            else:
                print(f"All passengers are ready to get off the train.")
                shared.unboarded.signal()
            self.barrier.signal(C)
            self.barrierCount = 0
        self.mutex.unlock()
        self.barrier.wait()


class Shared(object):
    """Class representing shared resources among savages and the cook."""
    def __init__(self):
        """Initializes the shared data."""
        self.boardQ = Semaphore(0)
        self.boardB = SimpleBarrier()
        self.boarded = Semaphore(0)
        self.unboardQ = Semaphore(0)
        self.unboardB = SimpleBarrier()
        self.unboarded = Semaphore(0)


def passenger_main(i, shared):
    """
    Function representing the behavior of a passenger.

    :param i: The identifier of the passenger
    :param shared: An instance of Shared containing shared resources
    """
    while True:
        shared.boardQ.wait()
        shared.boardB.wait(i, shared, 1)

        shared.unboardQ.wait()
        shared.unboardB.wait(i, shared, 0)


def car_main(shared):
    """
    Function representing the behavior of the train making the journey.

    :param shared: An instance of Shared containing shared resources
    """
    while True:
        print("The train is waiting until its capacity is filled.")
        shared.boardQ.signal(C)
        shared.boarded.wait()

        print("The train is running.")
        sleep(4)

        print("The train is waiting for all passengers to get off.")
        shared.unboardQ.signal(C)
        shared.unboarded.wait()


def main():
    """Main function to initialize and start the simulation."""
    shared = Shared()
    passenger = []

    car = Thread(car_main, shared)
    for i in range(N):
        passenger.append(Thread(passenger_main, i, shared))

    for t in passenger + [car]:
        t.join()


if __name__ == "__main__":
    main()
