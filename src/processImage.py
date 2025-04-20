import cv2
import numpy as np
from logging_config import logger
import getContours
import getHoughLines
import plot


def process_this_image_function(
    current_image_path: str, current_image_name: str
) -> None:
    if not current_image_path:
        logger.error("No valid image path!")
        return

    # Step 1: Read the image
    try:
        current_image: cv2.typing.MatLike = cv2.imread(current_image_path)
    except cv2.error as read_error:
        logger.error(f"Read Error at {current_image_name}: {read_error}")
        return

    # Step 2: Resize
    try:
        current_resized_image = cv2.resize(
            current_image,
            (1080, int(current_image.shape[0] * 1080 / current_image.shape[1])),
            cv2.INTER_LINEAR,
        )
        current_resize_image_plot = current_resized_image.copy()
    except cv2.error as resize_error:
        logger.error(f"Resize Error at {current_image_name}: {resize_error}")
        return

    # Step 3: Crop
    try:
        current_cropped_image_plot = current_resized_image[
            :, current_resized_image.shape[1] // 2 :
        ]
    except cv2.error as crop_error:
        logger.error(f"Crop Error at {current_image_name}: {crop_error}")
        return

    # Step 4: Grayscale
    try:
        grayscaled_image = cv2.cvtColor(current_cropped_image_plot, cv2.COLOR_BGR2GRAY)
    except cv2.error as grayscale_error:
        logger.error(f"Grayscale Error at {current_image_name}: {grayscale_error}")
        return

    # Step 5: OTSU threshold
    try:
        _, otsu_thresholded_image = cv2.threshold(
            grayscaled_image, 5, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
    except cv2.error as otsu_error:
        logger.error(f"Otsu Error at {current_image_name}: {otsu_error}")
        return

    # Step 6: Morphological Closing
    try:
        morph_kernel = np.ones((4, 4), np.uint8)
        morph_closed_image = cv2.morphologyEx(
            otsu_thresholded_image, cv2.MORPH_CLOSE, morph_kernel, iterations=10
        )
    except cv2.error as morph_error:
        logger.error(f"Noise Removal Error at {current_image_name}: {morph_error}")
        return

    # Step 7: Dilation
    try:
        dilation_kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(morph_closed_image, dilation_kernel, iterations=8)
    except cv2.error as dilation_error:
        logger.error(f"Dilation Error at {current_image_name}: {dilation_error}")
        return

    # Step 8: Canny Edge Detection
    try:
        canny_edges_image = getContours.get_Contours_Function(
            dilated_image, 100, 200, 3
        )
    except cv2.error as canny_error:
        logger.error(f"Canny Error at {current_image_name}: {canny_error}")
        return

    # Step 9: Hough Transform
    try:
        hough_image_plot = getHoughLines.get_hough_lines_function(
            canny_edges_image,
            current_cropped_image_plot,
            90,
            90,
            80,
            current_image_name,
        )
    except cv2.error as hough_error:
        logger.error(f"Hough Error at {current_image_name}: {hough_error}")
        return

    # Step 10: Plot
    try:
        plot.save_entire_process_plot(
            current_resize_image_plot,
            otsu_thresholded_image,
            morph_closed_image,
            dilated_image,
            canny_edges_image,
            hough_image_plot,
            current_image_name,
        )
    except Exception as plot_error:
        logger.error(f"Plot Error at {current_image_name}: {plot_error}")
        return

    # Final log messages
    logger.info(f"Finished processing image [{current_image_name}]")
    logger.info("--------------------")
