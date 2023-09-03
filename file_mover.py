import os
import shutil

images_source_dir = "data/arm/images/"
images_destination_dir = "data/arm/images_extras/"
labels_source_dir = "data/arm/labels/"
labels_destination_dir = "data/arm/labels_extras/"


def move_files(last_digit, source_dir, destination_dir):
    count = 0
    for file in os.listdir(source_dir):
        if file[-5] in last_digit:
            # print(file)
            count += 1
            source = source_dir + file
            destination = destination_dir + file
            print(source, "=>", destination)
            shutil.move(source, destination)
    print("\nCount:", count)

def align_labels_to_images_remove_extras():
    images = os.listdir(images_source_dir)
    count = 0
    for file in os.listdir(labels_source_dir):
        # print(file)
        dot = file.find(".")
        equivalent_image_file = file[0:dot] + ".png"
        equivalent_file_found = equivalent_image_file in images
        # print(file, dot, equivalent_image_file, equivalent_file_found)
        if not equivalent_file_found:
            source = labels_source_dir + file
            destination = labels_destination_dir + file
            print(source, "=>", destination)
            shutil.move(source, destination)
            count += 1
    print("\nMoved files:", count)

def align_labels_to_images_copy_missing_labels():
    labels = os.listdir(labels_destination_dir)
    count = 0
    for file in os.listdir(images_source_dir):
        # print(file)
        dot = file.find(".")
        equivalent_label_file = file[0:dot] + ".txt"
        equivalent_file_found = equivalent_label_file in labels
        # print(file, dot, equivalent_label_file, equivalent_file_found)
        if equivalent_file_found:
            source = labels_destination_dir + equivalent_label_file
            destination = labels_source_dir + equivalent_label_file
            print(source, "=>", destination)
            shutil.move(source, destination)
            count += 1
    print("\nMoved files:", count)


# last_digit = ["1", "3", "5", "7", "9"]
# move_files(last_digit=last_digit, source_dir=images_source_dir, destination_dir=images_destination_dir)

align_labels_to_images_copy_missing_labels()
align_labels_to_images_remove_extras()


def count_files(source_dir):
    print(len(os.listdir(source_dir)))



# count_files(images_source_dir)
# count_files(images_destination_dir)


