import random


def color_line():
    random_line_color = (int(random.randint(30, 255)), int(
        random.randint(40, 255)), int(random.randint(50, 255)))
    return random_line_color
