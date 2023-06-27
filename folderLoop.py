import os
import traceback
import processImage


def loop_folder_function():
    dataset_folder = os.getcwd() + "/Input/Complete_Dataset/"
    print('The DataSet Folder is: ' + dataset_folder)
    current_image_number = 1
    for current_image_name in sorted(os.listdir(dataset_folder)):
        # Folder loop:
        current_image_path = os.path.join(dataset_folder, current_image_name)
        print("currentImage is: " + current_image_path)
        if (current_image_name.endswith(".bmp")):
            print("The nr. " + str(current_image_number) +
                  " current image is: " + current_image_path)
            try:
                processImage.process_this_image_function(
                    current_image_path, current_image_name, current_image_number)
            except Exception as processing_exception:
                print("(!) EXCEPTION AT IMAGE PROCESSING: " + str(processing_exception))
                print("(!) TRACEBACK: " + traceback.format_exc())
            current_image_number = current_image_number + 1
        else:
            print("(!) img is not bmp! " + current_image_name)
