import cv2
import numpy as np
from logging_config import logger

CONTOUR_BLUR_KERNEL_SIZE = (9, 9)
CONTOUR_BLUR_SIGMA = 1
MIN_CONTOUR_ARC_LENGTH = 500


def get_contours(
    dilation_img: cv2.typing.MatLike,
    canny_threshold_1: int,
    canny_threshold_2: int,
    canny_aperture_size: int,
) -> cv2.typing.MatLike:
    """Perform edge detection and contour extraction."""

    if dilation_img is None:
        logger.error("No valid Dilation Image provided.")
        # Return an empty image in case of error
        return np.zeros((1, 1, 3), dtype=np.uint8)

    # Initialize blank image for drawing contours
    blank_image = np.zeros((dilation_img.shape[0], dilation_img.shape[1], 3), np.uint8)

    try:
        # Step 1: Apply Gaussian Blur to reduce noise
        blurred_image: cv2.typing.MatLike = cv2.GaussianBlur(
            dilation_img, CONTOUR_BLUR_KERNEL_SIZE, CONTOUR_BLUR_SIGMA
        )
    except cv2.error as blur_exception:
        logger.error(f"Error during GaussianBlur: {blur_exception}")
        return blank_image  # Return blank image on error

    try:
        # Step 2: Apply Canny edge detection
        canny_image: cv2.typing.MatLike = cv2.Canny(
            blurred_image, canny_threshold_1, canny_threshold_2, canny_aperture_size
        )
    except cv2.error as canny_exception:
        logger.error(f"Error during Canny edge detection: {canny_exception}")
        return blank_image  # Return blank image on error

    # Step 3: Find contours from the Canny edges
    contours, _ = cv2.findContours(
        canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Step 4: Draw contours on the blank image
    for contour in contours:
        contour_length = cv2.arcLength(contour, True)
        if contour_length > MIN_CONTOUR_ARC_LENGTH:  # Only draw sufficiently large contours
            cv2.drawContours(blank_image, [contour], -1, (255, 255, 255), 2)

    logger.info(f"Contours detected: {len(contours)}")
    return blank_image
