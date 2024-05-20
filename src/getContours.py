import cv2
import numpy as np


def get_Contours_Function(dilation_img:np.ndarray, threshold_1, threshold_2, kernel_size) -> np.ndarray | None:
    if ((dilation_img is None)):
        print("No valid Dilation Image")
    else:
        # edge detection:
        blank_image = np.zeros(
            (dilation_img.shape[0], dilation_img.shape[1], 3), np.uint8)
        try:
            blurred_image: cv2.typing.MatLike = cv2.GaussianBlur(dilation_img, (9, 9), 1)
        except cv2.error as blur_exception:
            print(blur_exception)
        try:
            canny_image: cv2.typing.MatLike = cv2.Canny(blurred_image, threshold_1,
                                 threshold_2, kernel_size)
        except cv2.error as canny_exception:
            print(canny_exception)
        contours, hierarchy = cv2.findContours(
            canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            len: float = cv2.arcLength(contour, True)
            if len > 500:
                contours_image: cv2.typing.MatLike = cv2.drawContours(
                    blank_image, contour, -1, (255, 255, 255), 2)
        return contours_image
