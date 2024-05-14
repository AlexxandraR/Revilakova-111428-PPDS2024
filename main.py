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
    """Main function to test class Event and method
    merge_rectangles(rectangles)"""
    filename = "rectangles8.txt"
    rectangles = []

    with open(filename, 'r') as file:
        for line in file:
            coordinates = line.strip().split(',')
            left_bottom = int(coordinates[0]), int(coordinates[1])
            right_top = int(coordinates[2]), int(coordinates[3])
            rectangles.append((left_bottom, right_top))

    events = []
    for left_bottom, right_top in rectangles:
        events.append(Event(left_bottom[0], True,
                            (left_bottom[1], right_top[1])))
        events.append(Event(right_top[0], False,
                            (left_bottom[1], right_top[1])))

    events.sort()
    all_rectangles = []

    for event in events:
        all_rectangles.append(event.y_range)

    print("Y-rozsah obdlznikov je:", merge_rectangles(all_rectangles))


if __name__ == "__main__":
    main()
