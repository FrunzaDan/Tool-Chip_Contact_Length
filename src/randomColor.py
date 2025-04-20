import random

# Constants for color range
MIN_VALUE = 120
MAX_VALUE = 255


def color_line() -> tuple[int, int, int]:
    """Generate a random RGB color within the specified range."""

    # Generate random values for Red, Green, and Blue within the defined range
    red = random.randint(MIN_VALUE, MAX_VALUE)
    green = random.randint(MIN_VALUE, MAX_VALUE)
    blue = random.randint(MIN_VALUE, MAX_VALUE)

    # Return the randomly generated color as a tuple
    return red, green, blue
