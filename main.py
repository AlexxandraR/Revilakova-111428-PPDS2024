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


def calculate_area(rectangles):
    """
    Calculate the area of rectangles using sequential sweep line
    algorithm.

    :param rectangles: Rectangles whose area must be calculated."""
    events = []
    for left_bottom, right_top in rectangles:
        events.append(Event(left_bottom[0], True,
                            (left_bottom[1], right_top[1])))
        events.append(Event(right_top[0], False,
                            (left_bottom[1], right_top[1])))

    events.sort()
    active_rectangles = []
    current_x = events[0].x
    area = 0
    active_height = 0

    for event in events:
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

    area = calculate_area(rectangles)
    print("Obsah plochy zaberanej obdĺžnikmi je:", area)


if __name__ == "__main__":
    main()
