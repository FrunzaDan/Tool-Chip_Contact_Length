import os
import cv2
import numpy as np
import folderLoop
from logging_config import logger

# Layout of the 2x3 diagnostic grid image.
GRID_ROWS = 2
GRID_COLS = 3
CELL_CONTENT_WIDTH = 380
CELL_CONTENT_HEIGHT = 300
CELL_TITLE_HEIGHT = 28
SUPTITLE_HEIGHT = 40
MARGIN = 6

BACKGROUND_COLOR = (245, 245, 245)  # light gray, BGR - grid background/gutters
PANEL_BACKGROUND_COLOR = (255, 255, 255)  # white - behind each letterboxed image

TITLE_FONT = cv2.FONT_HERSHEY_SIMPLEX
TITLE_FONT_SCALE = 0.6
TITLE_FONT_THICKNESS = 1
TITLE_COLOR = (0, 0, 0)

SUPTITLE_FONT_SCALE = 0.9
SUPTITLE_FONT_THICKNESS = 2


def _to_bgr(image: cv2.typing.MatLike) -> cv2.typing.MatLike:
    """Ensure image has 3 channels so it can be composited into a color grid."""
    if image.ndim == 2 or (image.ndim == 3 and image.shape[2] == 1):
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image


def _resize_to_fit(
    image: cv2.typing.MatLike, target_width: int, target_height: int
) -> cv2.typing.MatLike:
    """Resize image to fit within (target_width, target_height) preserving its
    aspect ratio, centered on a white canvas of exactly that size (letterboxed)."""
    src_height, src_width = image.shape[:2]
    scale = min(target_width / src_width, target_height / src_height)
    new_width = max(1, round(src_width * scale))
    new_height = max(1, round(src_height * scale))
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

    canvas = np.full((target_height, target_width, 3), PANEL_BACKGROUND_COLOR, dtype=np.uint8)
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    canvas[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = resized
    return canvas


def _make_panel(image: cv2.typing.MatLike, title: str) -> cv2.typing.MatLike:
    """Build one grid cell: a title bar over the aspect-preserved, letterboxed image."""
    panel = np.full(
        (CELL_TITLE_HEIGHT + CELL_CONTENT_HEIGHT, CELL_CONTENT_WIDTH, 3),
        PANEL_BACKGROUND_COLOR,
        dtype=np.uint8,
    )
    cv2.putText(
        panel,
        title,
        (4, CELL_TITLE_HEIGHT - 8),
        TITLE_FONT,
        TITLE_FONT_SCALE,
        TITLE_COLOR,
        TITLE_FONT_THICKNESS,
        cv2.LINE_AA,
    )
    fitted = _resize_to_fit(_to_bgr(image), CELL_CONTENT_WIDTH, CELL_CONTENT_HEIGHT)
    panel[CELL_TITLE_HEIGHT:, :] = fitted
    return panel


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
    Build a 2x3 diagnostic grid of the pipeline's intermediate images and save
    it as a PNG.

    This composites the grid directly with OpenCV (resize + tile + text)
    rather than matplotlib: profiling showed matplotlib's savefig() alone
    accounted for ~94% of total per-image processing time here, since this is
    plain image tiling with plain titles, not an actual data plot - the
    OpenCV approach produces the same 6-panel grid in roughly a quarter of
    the time.
    """
    images_and_titles = [
        (current_resize_image_plot, "Original"),
        (otsu_thresholded_image, "OTSU BINARY"),
        (morph_closed_image, "MORPH CLOSING: 4x4"),
        (dilated_image, "DILATION: 3x3"),
        (canny_edges_image, "CANNY"),
        (hough_image_plot, "HOUGH LINES"),
    ]

    panels = [_make_panel(image, title) for image, title in images_and_titles]
    panel_height, panel_width = panels[0].shape[:2]

    grid_width = GRID_COLS * panel_width + (GRID_COLS + 1) * MARGIN
    grid_height = SUPTITLE_HEIGHT + GRID_ROWS * panel_height + (GRID_ROWS + 1) * MARGIN
    canvas = np.full((grid_height, grid_width, 3), BACKGROUND_COLOR, dtype=np.uint8)

    cv2.putText(
        canvas,
        current_image_name,
        (MARGIN, SUPTITLE_HEIGHT - 12),
        TITLE_FONT,
        SUPTITLE_FONT_SCALE,
        TITLE_COLOR,
        SUPTITLE_FONT_THICKNESS,
        cv2.LINE_AA,
    )

    for index, panel in enumerate(panels):
        row, col = divmod(index, GRID_COLS)
        y = SUPTITLE_HEIGHT + MARGIN + row * (panel_height + MARGIN)
        x = MARGIN + col * (panel_width + MARGIN)
        canvas[y : y + panel_height, x : x + panel_width] = panel

    image_base_name, _ = os.path.splitext(current_image_name)
    output_folder_path = os.path.join(
        folderLoop.output_plot_results_folder, f"{image_base_name}.png"
    )

    try:
        success = cv2.imwrite(output_folder_path, canvas)
        if success:
            logger.info(f"Saved plot image: {output_folder_path}")
        else:
            logger.error(f"Failed to save plot image: {output_folder_path}")
    except Exception as e:
        logger.error(f"Error saving plot image for {current_image_name}: {e}")
