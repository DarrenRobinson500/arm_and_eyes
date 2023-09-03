import os
from PIL import Image, ImageTk
import cv2
from settings import *

# images = []

class OwnImage():
    def __init__(self, number, model, image_names):
        self.number = number
        self.model = model
        self.name = image_names[number]
        self.image_file = image_names[number]
        self.image_path = model.source_folder_images + "/" + self.image_file
        self.label_file = self.image_file[0:-4] + ".txt"
        self.label_path = model.source_folder_labels + "/" + self.label_file
        self.image = ImageTk.PhotoImage(Image.open(self.image_path))
        self.image_cv2 = cv2.imread(self.image_path)
        self.labels = []
        self.load_labels()
        self.box_list = []

        # for label in self.labels:
        #     print("Labels:", self.model, self.name, label)
        # images.append(self)

    def __str__(self):
        return self.image_file

    def include_in_training(self):
        return len(self.labels) > 0

    def has_label(self):
        return len(self.labels) > 0

    def get_label_list(self):
        label_list = []
        for label in self.labels:
            # print(label[0])
            result = label[0]
            if result not in label_list: label_list.append(result)
        # print(self.label_path, label_list)
        return label_list

    def add_label(self, class_id, x1, y1, x2, y2, w, h):
        x0, y0, w0, h0 = round(x1 / w, 3), round(y1 / h, 3), round((x2 - x1) / w, 3), round((y2 - y1) / h, 3)
        new_label = [class_id, x0, y0, w0, h0]
        # Check over-written labels
        for label in self.labels:
            id, x, y, w, h = label
            if x < x0 + w0 / 2 < x + w and y < y0 + h0 / 2 < y + h:
                self.labels.remove(label)
        # Add new label to internal list and external file
        self.labels.append(new_label)
        self.write_labels_to_file()

    def delete_label(self, x0, y0):
        x0, y0 = x0 / self.image.width(), y0 / self.image.height()
        change = False
        for label in self.labels:
            id, x, y, w, h = label
            if x < x0 < x + w and y < y0 < y + h:
                self.labels.remove(label)
                change = True
        if change:
            self.write_labels_to_file()

    def load_labels(self):
        if not os.path.exists(self.label_path):
            return

        f = open(self.label_path, "r")
        available_labels = []
        for label in self.model.labels:
            # print(type(label))
            available_labels.append(int(label.number))
        # print("Available labels:", available_labels)

        for line in f:
            label_no, x, y, w, h = line.strip().split()
            label_no = int(label_no)
            self.labels.append((int(label_no), float(x), float(y), float(w), float(h)))

            result = label_no in available_labels
            if not result:
                print(f"Label validation for '{self.image_file}':", label_no, result)
            # print(f"Label validation for '{self.image_file}':", label_no, result)


    # def delete_label(self, number):
    #     new_annotation = [class_id, round(x1 / w, 3), round(y1 / h, 3), round((x2 - x1) / w, 3), round((y2 - y1) / h, 3)]
    #     self.annotations.append(new_annotation)
    #     self.write_annotations_to_file()

    def write_labels_to_file(self):
        f = open(self.label_path, "w")
        f.truncate(0)
        for label in self.labels:
            label = str(label)[1:-1].replace(",", "")
            f.write(f"{label}\n")
        f.close()


# blank = OwnImage(0, None, ["blank"])
