from PIL import Image
import io
import folderLoop
from matplotlib import pyplot as plt


def plot_images(current_resize_image_plot, otsu_thresholded_image, morph_closed_image, dilated_image, canny_edges_image, hough_image_plot, current_image_name):
    # Plotting:
    can_plot = True
    if can_plot:
        plt.subplot(231), plt.imshow(current_resize_image_plot)
        plt.title("Original"), plt.xticks([]), plt.yticks([])
        plt.subplot(232), plt.imshow(otsu_thresholded_image, 'gray')
        plt.title("OTSU BINARY"), plt.xticks([]), plt.yticks([])
        plt.subplot(233), plt.imshow(morph_closed_image, 'gray')
        plt.title("MORPH CLOSING: 4x4"), plt.xticks([]), plt.yticks([])
        plt.subplot(234), plt.imshow(dilated_image, 'gray')
        plt.title("DILATION: 3x3"), plt.xticks([]), plt.yticks([])
        plt.subplot(235), plt.imshow(canny_edges_image, 'gray')
        plt.title("CANNY"), plt.xticks([]), plt.yticks([])
        plt.subplot(236), plt.imshow(hough_image_plot)
        plt.title("HOUGH LINES"), plt.xticks([]), plt.yticks([])

        # visualize:
        fig = plt.gcf()
        fig.canvas.manager.set_window_title(current_image_name)
        fig.suptitle(current_image_name, fontsize=14)
        plt.tight_layout()

        # Save the plot directly to disk (no memory buffer)
        try:
            output_folder_path = folderLoop.output_plot_results_folder + current_image_name
            plt.savefig(output_folder_path, format='png')
            print("- saved plot image: " + output_folder_path)
        except Exception as e:
            print(f"Error saving plot image: {e}")

        plt.close(fig)  # Close the figure after saving
