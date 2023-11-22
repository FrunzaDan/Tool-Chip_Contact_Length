import cv2
import numpy as np
from matplotlib import pyplot as plt
import getContours
import getHoughLines
import plot


def process_this_image_function(current_image_path, current_image_name, current_image_number):
    if current_image_path:
        # reads the image:
        try:
            current_image = cv2.imread(current_image_path)
        except cv2.error as read_error:
            print("Read Error at " + current_image_name + ": " + str(read_error))
        # resize the current image to 1080p:
        try:
            current_resized_image = cv2.resize(current_image, (1080, int(
                int(current_image.shape[0])*1080/int(current_image.shape[1]))), cv2.INTER_LINEAR)
            current_resize_image_plot = current_resized_image.copy()
        except cv2.error as resize_error:
            print("Resize Error at " + current_image_name +
                  ": " + str(resize_error))
        # Crop the Canny detected image in the right half:
        try:
            current_cropped_image_plot = current_resized_image[0:int(current_resized_image.shape[0]), int(
                current_resized_image.shape[1]/2):int(current_resized_image.shape[1])]
        except cv2.error as crop_error:
            print("Crop Error at " + current_image_name + ": " + str(crop_error))
        # grayscale the image:
        try:
            grayscaled_image = cv2.cvtColor(
                current_cropped_image_plot, cv2.COLOR_BGR2GRAY)
        except cv2.error as grayscale_Error:
            print("Grayscale Error at " + current_image_name +
                  ": " + str(grayscale_Error))
        # OTSU:
        try:
            ret, otsu_thresholded_image = cv2.threshold(
                grayscaled_image, 5, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        except cv2.error as otsu_Error:
            print("Otsu Error at " + current_image_name + ": " + str(otsu_Error))
        # Noise removal (MORPH CLOSING: 4x4):
        try:
            morphology_kernel = np.ones((4, 4), np.uint8)
            morph_closed_image = cv2.morphologyEx(
                otsu_thresholded_image, cv2.MORPH_CLOSE, morphology_kernel, iterations=10)
        except cv2.error as noise_removal_Error:
            print("Noise Removal Error at " + current_image_name +
                  ": " + str(noise_removal_Error))
        # Dilation (DILATION: 3x3):
        try:
            dilation_kernel = np.ones((3, 3), np.uint8)
            dilated_image = cv2.dilate(
                morph_closed_image, dilation_kernel, iterations=8)
        except cv2.error as dilation_error:
            print("Error at " + current_image_name + ": " + str(dilation_error))
        # Canny Edge Detection:
        try:
            canny_edges_image = getContours.get_Contours_Function(
                dilated_image, 100, 200, 3)
        except cv2.error as canny_error:
            print("Canny Error at " + current_image_name + ": " + str(canny_error))

        # HoughP Transform:
        try:
            hough_image_plot = getHoughLines.get_hough_lines_function(
                canny_edges_image, current_cropped_image_plot, 90, 90, 80, current_image_name, current_image_number)
        except cv2.error as hough_error:
            print("Hough Error at " + current_image_name + ": " + str(hough_error))
        # Plotting:
        try:
            plot.plot_images(current_resize_image_plot, otsu_thresholded_image,
                             morph_closed_image, dilated_image, canny_edges_image, hough_image_plot, current_image_name)
        except cv2.error as plot_error:
            print("Plot Error at " + current_image_name + ": " + str(plot_error))
    else:
        print("No valid image path!")
