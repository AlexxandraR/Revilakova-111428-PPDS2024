"""This module solves the second task by implementing a Simple Barrier."""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

from time import sleep
from fei.ppds import Thread, Semaphore, print, Mutex

D = 7
H = 10


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

    def wait(self, i, barrier_num):
        """
       Waits for all threads to arrive at the specified barrier.

       Args:
           i (int): The identifier of the thread.
           barrier_num (int): Barrier identification number.
       """
        self.mutex.lock()
        self.barrierCount += 1
        print(f"Savage {i} came to barrier {barrier_num}. Total number at barrier {barrier_num}: {self.barrierCount}.")
        if self.barrierCount == D:
            if barrier_num == 1:
                print(f"All savages are at barrier {barrier_num} and are starting to eat.")
            else:
                print(f"All savages are at barrier {barrier_num} and are leaving for barrier 1.")
            self.barrier.signal(D)
            self.barrierCount = 0
        self.mutex.unlock()
        self.barrier.wait()


class Shared(object):
    """Class representing shared resources among savages and the cook."""
    def __init__(self):
        """Initializes the shared data."""
        self.mutex = Mutex()
        self.portion = 0
        self.fullPot = Semaphore(0)
        self.emptyPot = Semaphore(0)
        self.barrier1 = SimpleBarrier()
        self.barrier2 = SimpleBarrier()


def eat(i, shared):
    """
    Function representing the action of savage eating food.

    Args:
        i (int): The identifier of the savage.
        shared (Shared): An instance of Shared containing shared resources.
    """
    shared.mutex.lock()
    if shared.portion == 0:
        print(f"The pot is empty. Savage {i} will wake up the cook.")
        shared.emptyPot.signal()
        shared.fullPot.wait()
    shared.portion -= 1
    print(f"Savage {i} eats. The remaining portions: {shared.portion}")
    sleep(2)
    shared.mutex.unlock()


def savage(i, shared):
    """
    Function representing the behavior of a savage.

    Args:
        i (int): The identifier of the savage.
        shared (Shared): An instance of Shared containing shared resources.
    """
    while True:
        shared.barrier1.wait(i, 1)
        print(f"Savage {i} has passed the barrier 1.")
        eat(i, shared)
        shared.barrier2.wait(i, 2)


def serving_food(shared):
    """
    Function representing the behavior of the cook serving food.

    Args:
        shared (Shared): An instance of Shared containing shared resources.
    """
    while True:
        shared.emptyPot.wait()
        shared.portion = H
        sleep(3)
        print(f"The cook added {H} portions to the pot.")
        shared.fullPot.signal()


def main():
    """Main function to initialize and start the simulation."""
    shared = Shared()
    savages = []

    cook = Thread(serving_food, shared)
    for i in range(D):
        savages.append(Thread(savage, i, shared))

    for t in savages + [cook]:
        t.join()


if __name__ == "__main__":
    main()
