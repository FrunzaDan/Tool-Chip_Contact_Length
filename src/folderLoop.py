import os
import traceback
import processImage
from logging_config import logger

# Define folder paths. os.path.join is used throughout (no hardcoded "/" or "\")
# so these paths are valid on Windows, Linux, and macOS alike.
input_dataset_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "Input", "Complete_Dataset"
)
output_hough_results_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "Output", "folder_hough_results"
)
output_plot_results_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "Output", "folder_plot_results"
)

# Ensure the output folders exist regardless of platform, so a fresh checkout
# (or one where they were deleted) doesn't fail on the first save.
os.makedirs(output_hough_results_folder, exist_ok=True)
os.makedirs(output_plot_results_folder, exist_ok=True)


def loop_folder_function() -> None:
    """Loop through the input dataset folder and process each BMP image."""
    logger.info(f"The input dataset folder is: {input_dataset_folder}")

    current_image_number = 1
    for current_image_name in sorted(os.listdir(input_dataset_folder)):
        current_image_path = os.path.join(input_dataset_folder, current_image_name)

        # Skip directories and non-BMP files
        if os.path.isdir(current_image_path):
            logger.info(f"Skipping directory: {current_image_name}")
            continue

        # Skip hidden/system files such as macOS's .DS_Store, without logging
        # them as an unexpected/warning-worthy non-BMP file.
        if current_image_name.startswith("."):
            logger.info(f"Skipping hidden/system file: {current_image_name}")
            continue

        if current_image_name.endswith(".bmp"):
            logger.info(
                f"The nr. {current_image_number} current image is: {current_image_path}"
            )

            try:
                processImage.process_this_image_function(
                    current_image_path, current_image_name
                )
            except Exception as processing_exception:
                logger.error(
                    f"Exception during image processing: {processing_exception}"
                )
                logger.error(f"Traceback: {traceback.format_exc()}")

            current_image_number += 1
        else:
            logger.warning(f"Skipping non-BMP image: {current_image_name}")
