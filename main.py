"""This module solves the first assignment."""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

from time import sleep
from fei.ppds import Thread, Semaphore, print

semaphore = Semaphore(0)


def sleeps(name):
    """
    Simulates sleeping.

    :param name: Name of the person sleeping
    """
    print(f"{name} sleeps.")
    sleep(2)


def hygiene(name):
    """
    Simulates maintaining hygiene.

    :param name: Name of the person maintaining hygiene
    """
    print(f"{name}´s hygiene.")
    sleep(1)


def eat(name):
    """
    Simulates eating.

    :param name: Name of the person eating
    """
    print(f"{name} eats.")
    sleep(2)


def call(name):
    """
    Simulates making a call.

    :param name: Name of the person making the call
    """
    print(f"{name} calls.")
    sleep(1)
    semaphore.signal()


def receive_call(name):
    """
    Simulates receiving a call.

    :param name: Name of the person receiving the call
    """
    semaphore.wait()
    print(f"{name} receives call.")
    sleep(1)


def jano_thread():
    """
    Jano's thread simulating his activities.
    """
    sleeps("Jano")
    hygiene("Jano")
    eat("Jano")
    call("Jano")


def fero_thread():
    """
    Fero's thread simulating his activities.
    """
    sleeps("Fero")
    hygiene("Fero")
    receive_call("Fero")
    eat("Fero")


jano = Thread(jano_thread)
fero = Thread(fero_thread)

jano.join()
fero.join()

print("Both finished their tasks.")
