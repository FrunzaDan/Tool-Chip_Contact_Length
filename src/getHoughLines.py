import cv2
import cv2.mat_wrapper
import numpy as np
import math
import randomColor
import folderLoop


def get_hough_lines_function(current_canny_image: cv2.typing.MatLike, original_Image, votes_valid_line, min_line_length, max_line_gap, current_image_name) -> cv2.typing.MatLike:
    original_image_copy: cv2.typing.MatLike = original_Image
    blank_image: np.ndarray = np.zeros(
        (current_canny_image.shape[0], current_canny_image.shape[1], 3), np.uint8)
    hough_image_plot: np.ndarray = blank_image.copy()

    # process:
    houghLines: cv2.typing.MatLike = define_hough_lines(
        current_canny_image, votes_valid_line, min_line_length, max_line_gap, hough_image_plot)
    cleaned_lines: cv2.typing.MatLike = clean_lines(houghLines)

    # calculate the tool-chip contact length (difference between the 2 lines):
    try:
        tuple_result_horizontal: tuple[int, cv2.typing.MatLike] | None = get_horizontal_line_Y_index(
            cleaned_lines, original_image_copy)
        tuple_result_vertical: tuple[int, cv2.typing.MatLike] | None = get_vertical_line_Y_index(
            cleaned_lines, current_canny_image, original_image_copy)
        if tuple_result_horizontal is None:
            print("Y Points not found on horizontal line!")
        elif tuple_result_vertical is None:
            print("Y Points not found on vertical line!")
        else:
            y_point_of_horizontal: int = tuple_result_horizontal[0]
            y_point_of_vertical: int = tuple_result_vertical[0]
            saved_hough_image: cv2.typing.MatLike = tuple_result_horizontal[1]
            if saved_hough_image is None:
                saved_hough_image = tuple_result_vertical[1]

            contact_length: int = y_point_of_horizontal - y_point_of_vertical

            save_images(current_image_name, saved_hough_image, contact_length)

    except cv2.error as error:
        print(error)
        print("Not computable!")

    return hough_image_plot


def define_hough_lines(current_canny_image, votes_valid_line, min_line_length, max_line_gap, hough_lines_plot) -> cv2.typing.MatLike:
    current_canny_image: cv2.typing.MatLike = cv2.cvtColor(
        current_canny_image, cv2.COLOR_BGR2GRAY)
    current_canny_image = cv2.GaussianBlur(current_canny_image, (3, 3), 1)
    hough_lines: cv2.typing.MatLike = cv2.HoughLinesP(
        current_canny_image, 1, np.pi/180, votes_valid_line, None, min_line_length, max_line_gap)
    for hough_line in hough_lines:
        x1, y1, x2, y2 = hough_line[0]
        cv2.line(hough_lines_plot, (x1, y1), (x2, y2), (255, 0, 0), 3)
    return hough_lines


def clean_lines(hough_lines: cv2.typing.MatLike) -> cv2.typing.MatLike:
    # line cleanup:
    cleaned_Lines: cv2.typing.MatLike = np.empty(shape=[0, 4], dtype=np.int32)
    for houghLine in hough_lines:
        alfa: int = math.degrees(math.atan2(
            houghLine[0][2]-houghLine[0][0], houghLine[0][3]-houghLine[0][1]))
        if len(cleaned_Lines) == 0:
            cleaned_Lines = np.append(cleaned_Lines, [houghLine[0]], axis=0)
            continue
        similar = False
        for cleaned_Line in cleaned_Lines:
            beta: int = math.degrees(math.atan2(
                cleaned_Line[2]-cleaned_Line[0], cleaned_Line[3]-cleaned_Line[1]))
            if abs(alfa-beta) <= 4.5:
                similar = True
                break
        if not similar:
            cleaned_Lines = np.append(cleaned_Lines, [houghLine[0]], axis=0)
    return cleaned_Lines


def get_vertical_line_Y_index(cleaned_lines: cv2.typing.MatLike, current_canny_image: cv2.typing.MatLike, original_image_copy: cv2.typing.MatLike) -> tuple[int, cv2.typing.MatLike] | None:
    color_vertical: tuple[int, int, int] = randomColor.color_line()
    for line in [cleaned_lines]:
        for x1, y1, x2, y2 in line:
            # VERTICAL:
            if (abs(x1-x2) < 4) and ((x1 > current_canny_image.shape[0]/2) or (x1 > current_canny_image.shape[0]/2)) and ((y1 > current_canny_image.shape[1]/2) or (x2 > current_canny_image.shape[1]/2)):
                # choose only lowest y point of line:
                if y2 > y1:
                    cv2.putText(original_image_copy, "Y2: " + str(y2), (x2-150, y2+40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_vertical, 3, cv2.LINE_AA)
                    y_point_of_vertical: int = y2
                    saved_hough_image: cv2.typing.MatLike = cv2.line(
                        original_image_copy, (x1, y1), (x2, y2), color_vertical, 3)
                    saved_hough_image = cv2.circle(
                        saved_hough_image, (x2, y2), 10, color_vertical, thickness=2, lineType=8, shift=0)
                else:
                    y_point_of_vertical: int = y1
                    cv2.putText(original_image_copy, "Y1: " + str(y1), (x1-150, y1+40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_vertical, 3, cv2.LINE_AA)
                    saved_hough_image: cv2.typing.MatLike = cv2.line(
                        original_image_copy, (x1, y1), (x2, y2), color_vertical, 3)
                    saved_hough_image = cv2.circle(
                        saved_hough_image, (x1, y1), 10, color_vertical, thickness=2, lineType=8, shift=0)
                return (y_point_of_vertical, saved_hough_image)
            pass


def get_horizontal_line_Y_index(cleaned_lines, original_image_copy) -> tuple[int, cv2.typing.MatLike] | None:
    color_horizontal: tuple[int, int, int] = randomColor.color_line()
    for line in [cleaned_lines]:
        for x1, y1, x2, y2 in line:
            # HORIZONTAL:
            if (abs(y1-y2) < 10):
                # choose only lowest y point of line:
                if y2 > y1:
                    y_point_of_horizontal: int = y2
                    cv2.putText(original_image_copy, "Y2: " + str(y2), (x2-20, y1-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_horizontal, 3, cv2.LINE_AA)
                    saved_hough_image: cv2.typing.MatLike = cv2.line(
                        original_image_copy, (x1, y1), (x2, y2), color_horizontal, 3)
                    saved_hough_image = cv2.circle(
                        saved_hough_image, (x2, y2), 10, color_horizontal, thickness=2, lineType=8, shift=0)
                elif y2 == y1:
                    y_point_of_horizontal: int = y1
                    cv2.putText(original_image_copy, "Y2: " + str(y2), (x2-20, y1-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_horizontal, 3, cv2.LINE_AA)
                    cv2.putText(original_image_copy, "Y1: " + str(y1), (x1+20, y1-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_horizontal, 3, cv2.LINE_AA)
                    saved_hough_image: cv2.typing.MatLike = cv2.line(
                        original_image_copy, (x1, y1), (x2, y2), color_horizontal, 3)
                    saved_hough_image = cv2.circle(
                        saved_hough_image, (x1, y1), 10, color_horizontal, thickness=2, lineType=8, shift=0)
                    saved_hough_image = cv2.circle(
                        saved_hough_image, (x2, y2), 10, color_horizontal, thickness=2, lineType=8, shift=0)
                else:
                    y_point_of_horizontal = y1
                    cv2.putText(original_image_copy, "Y1: " + str(y1), (x1+20, y1-30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_horizontal, 3, cv2.LINE_AA)
                    saved_hough_image: cv2.typing.MatLike = cv2.line(
                        original_image_copy, (x1, y1), (x2, y2), color_horizontal, 3)
                    saved_hough_image = cv2.circle(
                        saved_hough_image, (x1, y1), 10, color_horizontal, thickness=2, lineType=8, shift=0)
                return (y_point_of_horizontal, saved_hough_image)
            pass


def save_images(current_image_name: str, saved_hough_image: cv2.typing.MatLike, contact_length: int) -> None:

    output_folder_path: str = folderLoop.output_hough_results_folder + current_image_name
    color_contact_length: tuple[int, int, int] = randomColor.color_line()
    saved_hough_image = cv2.putText(saved_hough_image, "Dist = " + str(
        contact_length) + "px + t", (100, 100),  cv2.FONT_HERSHEY_SIMPLEX, 1.2, color_contact_length, 3, cv2.LINE_AA)
    cv2.imwrite(output_folder_path, saved_hough_image)
    print("- saved hough image: " + output_folder_path)
