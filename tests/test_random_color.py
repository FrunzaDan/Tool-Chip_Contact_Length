from randomColor import MAX_VALUE, MIN_VALUE, color_line


def test_color_line_channels_are_within_configured_range():
    for _ in range(50):
        red, green, blue = color_line()
        for channel in (red, green, blue):
            assert MIN_VALUE <= channel <= MAX_VALUE
