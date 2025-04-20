import cv2
import numpy as np
from logging_config import logger


def get_Contours_Function(
    dilation_img: cv2.typing.MatLike,
    threshold_1: float,
    threshold_2: float,
    kernel_size: float,
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
        blurred_image: cv2.typing.MatLike = cv2.GaussianBlur(dilation_img, (9, 9), 1)
    except cv2.error as blur_exception:
        logger.error(f"Error during GaussianBlur: {blur_exception}")
        return blank_image  # Return blank image on error

    try:
        # Step 2: Apply Canny edge detection
        canny_image: cv2.typing.MatLike = cv2.Canny(
            blurred_image, threshold_1, threshold_2, kernel_size
        )
    except cv2.error as canny_exception:
        logger.error(f"Error during Canny edge detection: {canny_exception}")
        return blank_image  # Return blank image on error

    # Step 3: Find contours from the Canny edges
    contours, hierarchy = cv2.findContours(
        canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Step 4: Draw contours on the blank image
    for contour in contours:
        contour_length = cv2.arcLength(contour, True)
        if contour_length > 500:  # Only draw contours that are sufficiently large
            cv2.drawContours(blank_image, [contour], -1, (255, 255, 255), 2)

    logger.info(f"Contours detected: {len(contours)}")
    return blank_image
