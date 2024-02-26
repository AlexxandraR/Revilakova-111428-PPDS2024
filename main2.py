"""This module solves the second task by implementing a Combining Tree Barrier."""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

from fei.ppds import Thread, Semaphore, print, Mutex
from math import log
from time import sleep


D = 7
H = 10


class CombiningTreeBarrier:
    """
    Implements a combining tree barrier.
    Implementation of this class was adapted from the example provided
    during the second seminar. Available at:
    https://github.com/tj314/ppds-seminars/blob/ppds2024/seminar2/combining_tree_barrier.py.
    """
    def __init__(self, num_threads):
        """Initializes the barrier with the number of threads."""
        if not log(num_threads + 1, 2).is_integer():
            print(f"Number threads N must be 2^k - 1")
            raise ValueError
        self.num_threads = num_threads
        self.in_semaphores = [Semaphore(0) for _ in range(num_threads)]
        self.out_semaphores = [Semaphore(0) for _ in range(num_threads)]

    @staticmethod
    def get_children(tid):
        """Returns the ids of the children of a node."""
        return 2*tid + 1, 2*tid + 2

    @staticmethod
    def is_leaf(tid, num_threads):
        """Returns True if the node is a leaf node."""
        return 2*tid + 1 >= num_threads

    def wait(self, tid):
        """Waits for all threads to arrive at the barrier."""
        if CombiningTreeBarrier.is_leaf(tid, self.num_threads):  # leaf node
            self.in_semaphores[tid].signal()
            self.out_semaphores[tid].wait()
        elif tid == 0:  # root node
            left_child, right_child = CombiningTreeBarrier.get_children(tid)
            self.in_semaphores[left_child].wait()
            self.in_semaphores[right_child].wait()
            print(f"All savages are at barrier and are starting to eat.")
            self.out_semaphores[left_child].signal()
            self.out_semaphores[right_child].signal()
        else:  # in between node
            left_child, right_child = CombiningTreeBarrier.get_children(tid)
            self.in_semaphores[left_child].wait()
            self.in_semaphores[right_child].wait()
            self.in_semaphores[tid].signal()
            self.out_semaphores[tid].wait()
            self.out_semaphores[left_child].signal()
            self.out_semaphores[right_child].signal()


class Shared(object):
    """Class representing shared resources among savages and the cook."""
    def __init__(self):
        """Initializes the shared data."""
        self.mutex = Mutex()
        self.portion = 0
        self.fullPot = Semaphore(0)
        self.emptyPot = Semaphore(0)
        self.barrier = CombiningTreeBarrier(D)


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
        print(f"Savage {i} came to barrier.")
        shared.barrier.wait(i)
        print(f"Savage {i} has passed the barrier.")
        eat(i, shared)


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
