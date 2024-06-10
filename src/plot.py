import folderLoop
from matplotlib import pyplot as plt


def create_subplot(image, title):
    plt.imshow(image, 'gray' if len(image.shape) == 2 else None)
    plt.title(title), plt.xticks([]), plt.yticks([])


def plot_images(current_resize_image_plot, otsu_thresholded_image, morph_closed_image,
                dilated_image, canny_edges_image, hough_image_plot, current_image_name) -> None:

    # Plotting:
    plt.subplot(231), create_subplot(current_resize_image_plot, "Original")
    plt.subplot(232), create_subplot(otsu_thresholded_image, "OTSU BINARY")
    plt.subplot(233), create_subplot(morph_closed_image, "MORPH CLOSING: 4x4")
    plt.subplot(234), create_subplot(dilated_image, "DILATION: 3x3")
    plt.subplot(235), create_subplot(canny_edges_image, "CANNY")
    plt.subplot(236), create_subplot(hough_image_plot, "HOUGH LINES")

    # Visualize:
    plt.suptitle(current_image_name, fontsize=16)
    plt.tight_layout()

    try:
        output_folder_path: str = folderLoop.output_plot_results_folder + current_image_name
        plt.savefig(output_folder_path, format='png')
        print("- saved plot image: " + output_folder_path)
    except Exception as e:
        print(f"Error saving plot image: {e}")

    plt.close()
