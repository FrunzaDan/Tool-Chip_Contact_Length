import cv2
import numpy as np
from logging_config import logger
import getContours
import getHoughLines
import plot

# Tunable pipeline parameters, named so they can all be found/adjusted in one
# place instead of as bare literals scattered through the function below.
RESIZE_WIDTH = 1080

OTSU_THRESHOLD_LOW = 5
OTSU_THRESHOLD_HIGH = 255

MORPH_CLOSE_KERNEL_SIZE = (4, 4)
MORPH_CLOSE_ITERATIONS = 10

DILATION_KERNEL_SIZE = (3, 3)
DILATION_ITERATIONS = 8

CANNY_THRESHOLD_1 = 100
CANNY_THRESHOLD_2 = 200
CANNY_APERTURE_SIZE = 3

HOUGH_VOTES_THRESHOLD = 90
HOUGH_MIN_LINE_LENGTH = 90
HOUGH_MAX_LINE_GAP = 80

# Sentinel distinguishing "the step raised and was already logged" from "the
# step legitimately returned None" (only the plot step does the latter).
_STEP_FAILED = object()


def _run_step(step_name: str, image_name: str, func, *args, **kwargs):
    """Run one pipeline step, logging and returning _STEP_FAILED on any exception."""
    try:
        return func(*args, **kwargs)
    except Exception as error:
        logger.error(f"{step_name} Error at {image_name}: {error}")
        return _STEP_FAILED


def _resize_to_fixed_width(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    target_height = int(image.shape[0] * RESIZE_WIDTH / image.shape[1])
    return cv2.resize(image, (RESIZE_WIDTH, target_height), cv2.INTER_LINEAR)


def _crop_right_half(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """Keep only the right half of the frame, where the tool-chip interface is.

    A real copy (not a numpy view) is returned so that later drawing on this
    image (the Hough-line annotations) can never silently mutate `image` itself.
    """
    return image[:, image.shape[1] // 2 :].copy()


def _apply_otsu_threshold(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    _, thresholded = cv2.threshold(
        image,
        OTSU_THRESHOLD_LOW,
        OTSU_THRESHOLD_HIGH,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )
    return thresholded


def _apply_morphological_closing(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    kernel = np.ones(MORPH_CLOSE_KERNEL_SIZE, np.uint8)
    return cv2.morphologyEx(
        image, cv2.MORPH_CLOSE, kernel, iterations=MORPH_CLOSE_ITERATIONS
    )


def _apply_dilation(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    kernel = np.ones(DILATION_KERNEL_SIZE, np.uint8)
    return cv2.dilate(image, kernel, iterations=DILATION_ITERATIONS)


def process_this_image_function(
    current_image_path: str, current_image_name: str
) -> None:
    if not current_image_path:
        logger.error("No valid image path!")
        return

    # Step 1: Read the image
    current_image = _run_step(
        "Read", current_image_name, cv2.imread, current_image_path
    )
    if current_image is _STEP_FAILED:
        return
    # cv2.imread does not raise on failure (bad path, corrupt/unsupported file);
    # it returns None, so this must be checked explicitly.
    if current_image is None:
        logger.error(
            f"Could not read image (missing, corrupt, or unsupported format): "
            f"{current_image_name}"
        )
        return

    # Step 2: Resize
    current_resized_image: cv2.typing.MatLike = _run_step(
        "Resize", current_image_name, _resize_to_fixed_width, current_image
    )
    if current_resized_image is _STEP_FAILED:
        return

    # Step 3: Crop
    current_cropped_image: cv2.typing.MatLike = _run_step(
        "Crop", current_image_name, _crop_right_half, current_resized_image
    )
    if current_cropped_image is _STEP_FAILED:
        return

    # Step 4: Grayscale
    grayscaled_image: cv2.typing.MatLike = _run_step(
        "Grayscale",
        current_image_name,
        cv2.cvtColor,
        current_cropped_image,
        cv2.COLOR_BGR2GRAY,
    )
    if grayscaled_image is _STEP_FAILED:
        return

    # Step 5: OTSU threshold
    otsu_thresholded_image: cv2.typing.MatLike = _run_step(
        "Otsu", current_image_name, _apply_otsu_threshold, grayscaled_image
    )
    if otsu_thresholded_image is _STEP_FAILED:
        return

    # Step 6: Morphological Closing
    morph_closed_image: cv2.typing.MatLike = _run_step(
        "Noise Removal",
        current_image_name,
        _apply_morphological_closing,
        otsu_thresholded_image,
    )
    if morph_closed_image is _STEP_FAILED:
        return

    # Step 7: Dilation
    dilated_image: cv2.typing.MatLike = _run_step(
        "Dilation", current_image_name, _apply_dilation, morph_closed_image
    )
    if dilated_image is _STEP_FAILED:
        return

    # Step 8: Canny Edge Detection
    canny_edges_image: cv2.typing.MatLike = _run_step(
        "Canny",
        current_image_name,
        getContours.get_contours,
        dilated_image,
        CANNY_THRESHOLD_1,
        CANNY_THRESHOLD_2,
        CANNY_APERTURE_SIZE,
    )
    if canny_edges_image is _STEP_FAILED:
        return

    # Step 9: Hough Transform
    hough_image_plot: cv2.typing.MatLike = _run_step(
        "Hough",
        current_image_name,
        getHoughLines.get_hough_lines_function,
        canny_edges_image,
        current_cropped_image,
        HOUGH_VOTES_THRESHOLD,
        HOUGH_MIN_LINE_LENGTH,
        HOUGH_MAX_LINE_GAP,
        current_image_name,
    )
    if hough_image_plot is _STEP_FAILED:
        return

    # Step 10: Plot
    plot_result = _run_step(
        "Plot",
        current_image_name,
        plot.save_entire_process_plot,
        current_resized_image,
        otsu_thresholded_image,
        morph_closed_image,
        dilated_image,
        canny_edges_image,
        hough_image_plot,
        current_image_name,
    )
    if plot_result is _STEP_FAILED:
        return

    # Final log messages
    logger.info(f"Finished processing image [{current_image_name}]")
    logger.info("--------------------")
