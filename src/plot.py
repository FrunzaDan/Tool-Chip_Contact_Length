import numpy as np
import folderLoop
from matplotlib import pyplot as plt
from logging_config import logger
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend


def save_entire_process_plot(
    current_resize_image_plot,
    otsu_thresholded_image,
    morph_closed_image,
    dilated_image,
    canny_edges_image,
    hough_image_plot,
    current_image_name,
) -> None:
    """
    Plot multiple image transformations in subplots and save the output as a PNG file.
    Optimized for speed when processing completely new images in each iteration.
    """
    # Create figure with optimal size once
    fig, axes = plt.subplots(2, 3, figsize=(12, 8), dpi=100)

    # Define image-title pairs for consistent processing
    images_and_titles = [
        (current_resize_image_plot, "Original"),
        (otsu_thresholded_image, "OTSU BINARY"),
        (morph_closed_image, "MORPH CLOSING: 4x4"),
        (dilated_image, "DILATION: 3x3"),
        (canny_edges_image, "CANNY"),
        (hough_image_plot, "HOUGH LINES"),
    ]

    # Process all subplots in a single optimized loop
    for ax, (img, title) in zip(axes.flat, images_and_titles):
        # Fast check for grayscale
        is_grayscale = len(img.shape) == 2 or (
            len(img.shape) == 3 and img.shape[2] == 1
        )

        # Display image with minimal overhead
        ax.imshow(img, cmap="gray" if is_grayscale else None, interpolation="nearest")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])

    # Add super title efficiently
    fig.suptitle(current_image_name, fontsize=16)

    # Use tight_layout with specific parameters to avoid recalculation
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    try:
        # Construct output path once
        output_folder_path = (
            f"{folderLoop.output_plot_results_folder}{current_image_name}"
        )

        # Save with optimized parameters for speed
        fig.savefig(
            output_folder_path,
            format="png",
            dpi=100,
            bbox_inches=None,  # Skip the computation-heavy tight bbox calculation
            pad_inches=0.1,
        )

        logger.info(f"Saved plot image: {output_folder_path}")

    except Exception as e:
        logger.error(f"Error saving plot image for {current_image_name}: {e}")

    # Close the figure to prevent memory leaks
    plt.close(fig)
