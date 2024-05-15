"""
This is the code for testing the semester assignment.
The solution was inspired by the presentation from lecture 11
(available at:
https://elearn.elf.stuba.sk/moodle/pluginfile.php/77449/mod_resource/content/1/Prednaska_12.pdf)
and by video Sweep Line Algorithm (available at:
https://www.youtube.com/watch?v=9wy6OA3Yvpg).
"""

__authors__ = "Alexandra Reviľáková"
__license__ = "MIT"

import sys
from mpi4py import MPI
import numpy as np

MASTER = 0


class Event:
    """
    Represents an event point in the sweep line algorithm.

    :param x: The x-coordinate of the event point.
    :param is_start: A boolean indicating whether the event point
    represents the start of a rectangle.
    :param y_range: A tuple representing the range of y-coordinates of
    the rectangle.
    """
    def __init__(self, x, is_start, y_range):
        self.x = x
        self.is_start = is_start
        self.y_range = y_range

    def __lt__(self, other):
        return self.x < other.x


def calculate_area(filename):
    """
    Calculate the area of rectangles defined in a file using the sweep
    line algorithm.

    :param filename: The name of the file containing rectangle
    coordinates.
    """
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nproc = comm.Get_size()

    events = []
    start_time = 0

    if rank == MASTER:
        start_time = MPI.Wtime()

        rectangles = []

        with open(filename, 'r') as file:
            for line in file:
                coordinates = line.strip().split(',')
                left_bottom = int(coordinates[0]), int(coordinates[1])
                right_top = int(coordinates[2]), int(coordinates[3])
                rectangles.append((left_bottom, right_top))

        for left_bottom, right_top in rectangles:
            events.append(Event(left_bottom[0], True,
                                (left_bottom[1], right_top[1])))
            events.append(Event(right_top[0], False,
                                (left_bottom[1], right_top[1])))

        events.sort()

    events = comm.bcast(events, root=MASTER)

    if nproc > len(events):
        if rank == 0:
            print(f"The number of processes must be less or equal to "
                  f"{len(events)}.")
        return

    lines = np.zeros(nproc, dtype=np.int64)
    offsets = np.zeros(nproc + 1, dtype=np.int64)
    active_rectangles1 = None

    if rank == MASTER:
        lines_num = len(events) // nproc
        extra_lines = len(events) % nproc
        offset = 0

        for proc in range(nproc):
            if proc < extra_lines:
                lines[proc] = lines_num + 1
            else:
                lines[proc] = lines_num
            offsets[proc] = offset
            offset += lines[proc]
        offsets[nproc] = len(events)

        active_rectangles1 = calculate_active_rectangles(events)
        active_rectangles1_copy = active_rectangles1[:]
        active_rectangles1 = [[]]
        for i in offsets[1:len(offsets) - 1]:
            active_rectangles1.append(active_rectangles1_copy[i - 1])

    offsets = comm.bcast(offsets, root=MASTER)
    active_rectangles = comm.scatter(active_rectangles1, root=MASTER)

    area = calculate_area_between_events(events, offsets[rank],
                                         offsets[rank + 1] + 1,
                                         active_rectangles)

    final_area = comm.gather(area, root=MASTER)

    if rank == MASTER:
        final_area = sum(final_area)

        end_time = MPI.Wtime()
        duration = end_time - start_time
        with open("output.txt", 'a') as subor:
            subor.write("{:.6f}".format(duration) + '\n')


def calculate_active_rectangles(events):
    """
    Calculate active rectangles at each event point.

    :param events: List of event points sorted by x-coordinate.
    :return: List of active rectangles at each event point.
    """
    active_rectangles_list = []
    active_rectangles = []

    for j in range(0, len(events)):
        event = events[j]
        if event.is_start:
            active_rectangles.append(event.y_range)
            active_rectangles.sort()
        else:
            active_rectangles.remove(event.y_range)
        active_rectangles_list.append(active_rectangles[:])
    return active_rectangles_list


def calculate_area_between_events(events, start_index, end_index,
                                  active_rectangles):
    """
    Calculate the area between two event points.

    :param events: List of event points sorted by x-coordinate.
    :param start_index: Index of the starting event point.
    :param end_index: Index of the ending event point.
    :param active_rectangles: List of active rectangles at each event
    point.
    :return: The area between the event points.
    """
    current_x = events[start_index].x
    active_height = 0
    area = 0
    for event in events[start_index:end_index]:
        dx = event.x - current_x
        current_x = event.x
        area += dx * active_height
        if event.is_start:
            active_rectangles.append(event.y_range)
            active_rectangles.sort()
            active_height = merge_rectangles(active_rectangles)
        else:
            active_rectangles.remove(event.y_range)
            active_height = merge_rectangles(active_rectangles)
    return area


def merge_rectangles(rectangles):
    """
    Merge overlapping rectangles.

    :param rectangles: List of rectangles represented as tuples of
    y-coordinates.
    :return: The total height of merged rectangles.
    """
    merged = []
    for rect in rectangles:
        if not merged or rect[0] > merged[-1][1]:
            merged.append(rect)
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], rect[1]))
    return abs(sum(y2 - y1 for y1, y2 in merged))


def main():
    """Main function to execute the program."""
    if len(sys.argv) != 2:
        print("Usage: python main_test.py rectangles_file.txt")
        return
    for i in range(100):
        calculate_area(sys.argv[1])


if __name__ == "__main__":
    main()
