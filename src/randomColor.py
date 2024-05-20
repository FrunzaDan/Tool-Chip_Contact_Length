import random

MIN_VALUE = 120
MAX_VALUE = 255


def color_line() -> tuple[int, int, int]:
    random_line_color: tuple[int, int, int] = (
        int(random.randint(MIN_VALUE, MAX_VALUE)),
        int(random.randint(MIN_VALUE, MAX_VALUE)),
        int(random.randint(MIN_VALUE, MAX_VALUE)),
    )
    return random_line_color
