import os
import cv2
import numpy as np
import math
import randomColor
import folderLoop
from logging_config import logger

# Line-classification thresholds.
ANGLE_SIMILARITY_THRESHOLD_DEGREES = 4.5
VERTICAL_LINE_MAX_DX = 4
HORIZONTAL_LINE_MAX_DY = 10

# Annotation drawing constants.
LINE_THICKNESS = 3
MARKER_RADIUS = 10
MARKER_THICKNESS = 2
FONT_SCALE = 1.2
FONT_THICKNESS = 3


def get_hough_lines_function(
    current_canny_image: cv2.typing.MatLike,
    original_image: cv2.typing.MatLike,
    votes_valid_line: int,
    min_line_length: int,
    max_line_gap: int,
    current_image_name: str,
) -> cv2.typing.MatLike:
    # NOTE: this function draws directly onto (mutates) `original_image` as
    # part of computing the contact length - it is not treated as read-only.
    blank_image: np.ndarray = np.zeros(
        (current_canny_image.shape[0], current_canny_image.shape[1], 3), np.uint8
    )
    hough_image_plot: np.ndarray = blank_image.copy()

    hough_lines: cv2.typing.MatLike | None = define_hough_lines(
        current_canny_image,
        votes_valid_line,
        min_line_length,
        max_line_gap,
        hough_image_plot,
    )
    if hough_lines is None:
        logger.warning(
            f"No Hough lines detected for {current_image_name}; "
            "skipping contact-length calculation."
        )
        return hough_image_plot

    cleaned_lines: cv2.typing.MatLike = clean_lines(hough_lines)

    # calculate the tool-chip contact length (difference between the 2 lines):
    try:
        horizontal_result: tuple[int, cv2.typing.MatLike] | None = (
            get_horizontal_line_Y_index(cleaned_lines, original_image)
        )
        vertical_result: tuple[int, cv2.typing.MatLike] | None = (
            get_vertical_line_Y_index(cleaned_lines, current_canny_image, original_image)
        )
        if horizontal_result is None:
            logger.warning("Y Points not found on horizontal line!")
        elif vertical_result is None:
            logger.warning("Y Points not found on vertical line!")
        else:
            # Both results reference the same (mutated) `original_image`, so
            # either one already carries both annotations.
            y_point_of_horizontal, annotated_image = horizontal_result
            y_point_of_vertical, _ = vertical_result

            contact_length: int = y_point_of_horizontal - y_point_of_vertical

            if contact_length <= 0:
                logger.warning(
                    f"{current_image_name}: computed contact length is "
                    f"non-positive ({contact_length}px) - likely horizontal/"
                    "vertical line misclassification, result is suspect."
                )

            save_result_image(current_image_name, annotated_image, contact_length)

    except cv2.error as error:
        logger.warning(f"Not computable! OpenCV error: {error}")

    return hough_image_plot


def define_hough_lines(
    current_canny_image: cv2.typing.MatLike,
    votes_valid_line: int,
    min_line_length: int,
    max_line_gap: int,
    hough_lines_plot: cv2.typing.MatLike,
) -> cv2.typing.MatLike | None:
    current_canny_image: cv2.typing.MatLike = cv2.cvtColor(
        current_canny_image, cv2.COLOR_BGR2GRAY
    )
    current_canny_image = cv2.GaussianBlur(current_canny_image, (3, 3), 1)
    hough_lines: cv2.typing.MatLike | None = cv2.HoughLinesP(
        current_canny_image,
        1,
        np.pi / 180,
        votes_valid_line,
        None,
        min_line_length,
        max_line_gap,
    )
    # cv2.HoughLinesP returns None (not an empty array) when no lines are found.
    if hough_lines is None:
        return None
    for hough_line in hough_lines:
        x1, y1, x2, y2 = hough_line[0]
        cv2.line(hough_lines_plot, (x1, y1), (x2, y2), (255, 0, 0), 3)
    return hough_lines


def clean_lines(hough_lines: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """Collapse near-duplicate Hough line segments, keeping one line per distinct angle."""
    cleaned_lines: list[tuple[int, int, int, int]] = []
    for hough_line in hough_lines:
        x1, y1, x2, y2 = hough_line[0]
        angle = math.degrees(math.atan2(x2 - x1, y2 - y1))
        is_duplicate_angle = any(
            abs(angle - math.degrees(math.atan2(cx2 - cx1, cy2 - cy1)))
            <= ANGLE_SIMILARITY_THRESHOLD_DEGREES
            for cx1, cy1, cx2, cy2 in cleaned_lines
        )
        if not is_duplicate_angle:
            cleaned_lines.append((x1, y1, x2, y2))

    if not cleaned_lines:
        return np.empty((0, 4), dtype=np.int32)
    return np.array(cleaned_lines, dtype=np.int32)


def _draw_point_label(
    image: cv2.typing.MatLike,
    marker_point: tuple[int, int],
    text_point: tuple[int, int],
    label: str,
    value: int,
    color: tuple[int, int, int],
) -> None:
    """Draw a labeled circle marker at marker_point, with the label's text at
    text_point (the two can differ - see callers). Mutates image in place."""
    cv2.putText(
        image,
        f"{label}: {value}",
        text_point,
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE,
        color,
        FONT_THICKNESS,
        cv2.LINE_AA,
    )
    cv2.circle(
        image,
        marker_point,
        MARKER_RADIUS,
        color,
        thickness=MARKER_THICKNESS,
        lineType=8,
        shift=0,
    )


def get_vertical_line_Y_index(
    cleaned_lines: cv2.typing.MatLike,
    current_canny_image: cv2.typing.MatLike,
    image: cv2.typing.MatLike,
) -> tuple[int, cv2.typing.MatLike] | None:
    color: tuple[int, int, int] = randomColor.color_line()

    # NOTE: threshold_a is compared against x-coordinates and threshold_b
    # against y/x-coordinates, using shape[0] (height) and shape[1] (width)
    # respectively - this looks like a height/width mix-up at a glance. It was
    # tested against the real dataset: "fixing" it to the dimensionally
    # "correct" shape[1]/shape[0] rejects the actual tool edge (which sits in
    # the upper portion of the cropped frame) and regresses detection. Left as
    # the original, empirically working thresholds.
    threshold_a = current_canny_image.shape[0] / 2
    threshold_b = current_canny_image.shape[1] / 2

    for x1, y1, x2, y2 in cleaned_lines:
        is_vertical = abs(x1 - x2) < VERTICAL_LINE_MAX_DX
        meets_position_thresholds = ((x1 > threshold_a) or (x2 > threshold_a)) and (
            (y1 > threshold_b) or (x2 > threshold_b)
        )
        if not (is_vertical and meets_position_thresholds):
            continue

        # The connecting line is the same regardless of which endpoint is lowest.
        cv2.line(image, (x1, y1), (x2, y2), color, LINE_THICKNESS)

        # choose only the lowest y point of the line:
        if y2 > y1:
            _draw_point_label(image, (x2, y2), (x2 - 150, y2 + 40), "Y2", y2, color)
            return y2, image
        else:
            _draw_point_label(image, (x1, y1), (x1 - 150, y1 + 40), "Y1", y1, color)
            return y1, image

    return None


def get_horizontal_line_Y_index(
    cleaned_lines: cv2.typing.MatLike, image: cv2.typing.MatLike
) -> tuple[int, cv2.typing.MatLike] | None:
    color: tuple[int, int, int] = randomColor.color_line()

    for x1, y1, x2, y2 in cleaned_lines:
        if abs(y1 - y2) >= HORIZONTAL_LINE_MAX_DY:
            continue

        # The connecting line is the same regardless of which endpoint(s) are lowest.
        cv2.line(image, (x1, y1), (x2, y2), color, LINE_THICKNESS)

        # choose only the lowest y point of the line (both, if they're equal):
        if y2 > y1:
            _draw_point_label(image, (x2, y2), (x2 - 20, y1 - 30), "Y2", y2, color)
            return y2, image
        elif y2 == y1:
            _draw_point_label(image, (x2, y2), (x2 - 20, y1 - 30), "Y2", y2, color)
            _draw_point_label(image, (x1, y1), (x1 + 20, y1 - 30), "Y1", y1, color)
            return y1, image
        else:
            _draw_point_label(image, (x1, y1), (x1 + 20, y1 - 30), "Y1", y1, color)
            return y1, image

    return None


def save_result_image(
    current_image_name: str, saved_hough_image: cv2.typing.MatLike, contact_length: int
) -> None:
    output_folder_path = os.path.join(
        folderLoop.output_hough_results_folder, current_image_name
    )

    color_contact_length = randomColor.color_line()
    text = f"Dist = {contact_length}px + t"

    cv2.putText(
        saved_hough_image,
        text,
        (100, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE,
        color_contact_length,
        FONT_THICKNESS,
        cv2.LINE_AA,
    )

    success = cv2.imwrite(output_folder_path, saved_hough_image)

    if success:
        logger.info(f"Saved hough image: {output_folder_path}")
    else:
        logger.error(f"Failed to save image: {output_folder_path}")
