import random

MIN_VALUE = 120
MAX_VALUE = 255

def color_line():
    random_line_color = (
        int(random.randint(MIN_VALUE, MAX_VALUE)),
        int(random.randint(MIN_VALUE, MAX_VALUE)),
        int(random.randint(MIN_VALUE, MAX_VALUE)),
    )
    return random_line_color
