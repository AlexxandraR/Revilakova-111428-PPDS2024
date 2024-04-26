import numpy as np


class Scheduler:
    def __init__(self):
        self._jobs = []

    def add_job(self, it):
        self._jobs.append(it)

    def start(self, data):
        counter = 0
        finished_coroutine_counter = 0
        while self._jobs:
            for i, job in enumerate(self._jobs):
                try:
                    if counter < len(data[0]):
                        next(job)
                        job.send(data[counter // len(data[0])])
                        counter += 1
                    elif counter < len(data[0]) * len(data):
                        job.send(data[counter // len(data[0])])
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


def coroutine1():
    try:
        while True:
            data = yield
            print("Coroutine 1:", data[0])
    except GeneratorExit:
        print("Stops coroutine 1")


def coroutine2():
    try:
        while True:
            data = yield
            print("Coroutine 2:", data[1])
    except GeneratorExit:
        print("Stops coroutine 2")


def coroutine3():
    try:
        while True:
            data = yield
            print("Coroutine 3:", data[2])
    except GeneratorExit:
        print("Stops coroutine 3")


def check_subarrays_length(data):
    for subarray in data:
        if len(subarray) != 3:
            return False
    return True


def main():
    scheduler = Scheduler()
    it1 = coroutine1()
    scheduler.add_job(it1)
    it2 = coroutine2()
    scheduler.add_job(it2)
    it3 = coroutine3()
    scheduler.add_job(it3)
    data = [["Ide", "piesen", "dokola,"], ["okolo", "stola", "-la -la ..."]]
    if not check_subarrays_length(data):
        print("All subarrays must have a length of 3.")
    else:
        try:
            np_data = np.array(data)
            scheduler.start(np_data)
        except ValueError:
            print("The array data has an inhomogeneous shape after 1 "
                  "dimensions.")


if __name__ == "__main__":
    main()
