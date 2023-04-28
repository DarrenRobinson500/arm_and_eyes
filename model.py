from ultralytics import YOLO
import os
import shutil
from datetime import datetime, timedelta
now = datetime.now
from utilities import *

from images import *
from labels import *
from run import *

models = []

'''
Things to add to model
 - Configurable model size
 - Configurable threshold
 - Model train log that retains (model size, epochs, training time, mAP50, mAP95, training number)
'''



def make_dir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def integers(list):
    new_list = []
    for item in list: new_list.append(int(item))
    return new_list

def delete_files(folder):
    for filename in os.listdir(folder):
        os.remove(folder + "/" + filename)

class Model:
    def __init__(self, name, initial_setup=True):
        self.number = len(models)
        self.name = name
        self.labels = []
        self.runs = []

        # Folders and Paths
        self.video_folder = "videos/" + self.name
        self.video_folder_done = "videos/" + self.name + "/done"
        self.source_folder = "data/" + self.name
        self.source_folder_images = self.source_folder + "/images"
        self.source_folder_labels = self.source_folder + "/labels"
        self.list_of_labels_path = self.source_folder + "/labels/list_of_labels.txt"
        self.model_folder = "models/" + self.name
        self.model_folder_images = self.model_folder + "/images"
        self.model_folder_labels = self.model_folder + "/labels"
        self.model_path = self.model_folder + "/" + self.name + ".pt"
        self.yaml_path = self.model_folder + "/" + self.name + ".yaml"
        self.boxes_path = self.model_folder + "/boxes.txt"
        self.trash_path = "trash/" + self.name
        self.folders = [
            self.source_folder, self.source_folder_images, self.source_folder_labels, self.model_folder,
            self.model_folder_labels, self.model_folder_images, self.video_folder, self.video_folder_done,
        ]

        models.append(self)
        if initial_setup:
            self.create_folders()
            write_models_to_file()
            self.save_size("medium")
            self.save_threshold(0.5)
            self.save_epochs(200)
            self.time = 0
            self.map50 = 0
            self.map95 = 0
        else:
            self.load_details()

        self.images = []
        self.load_images()
        self.load_runs()
        self.initiate_labels()
        self.load_boxes()

    def __str__(self):
        return f"{self.name}"

    def print_paths(self):
        print("Name:                  ", self.name)
        print("Source folder:         ", self.source_folder)
        print("Source folder (images):", self.source_folder_images)
        print("Source folder (labels):", self.source_folder_labels)
        print("List of labels:        ", self.list_of_labels_path)
        print("Model folder:          ", self.model_folder)
        print("Model folder (images): ", self.model_folder_images)
        print("Model folder (labels): ", self.model_folder_labels)
        print("Model path:            ", self.model_path)
        print("YAML path:             ", self.yaml_path)

    def load_details(self):
        self.size = db_read(self.name, "size")
        epochs = db_read(self.name, "epochs")
        if epochs: self.epochs = int(epochs)
        else: self.epochs = None
        self.threshold = db_read(self.name, "threshold")
        self.map50 = db_read(self.name, "map50")
        self.map95 = db_read(self.name, "map95")
        self.time = db_read(self.name, "time")

    def get_first_image(self):
        if len(self.images) > 0:
            return self.images[0]
        return None

    def create_folders(self):
        for folder in self.folders:
            print("Create folder:", folder)
            make_dir(folder)

    def delete_folders(self):
        make_dir(self.trash_path)
        for folder in self.folders:
            source = folder
            destination = self.trash_path + "/" + source
            if os.path.exists(source):
                try:
                    if os.path.exists(destination): delete_files(destination)
                except: pass
                try:
                    shutil.move(source, destination)
                except: pass

    def available_videos(self):
        result = ""
        make(self.video_folder)
        # print("Available videos folder:", self.video_folder)
        for filename in os.listdir(self.video_folder):
            if filename != "done":
                result = result + filename + " "
        if result == "": result = f"[{self.video_folder}]"
        return result

    def load_videos(self):
        make_dir(self.video_folder_done)
        video_count = 0
        for filename in os.listdir(self.video_folder):
            if filename == "done": continue
            source = self.video_folder + "/" + filename
            cap = cv2.VideoCapture(source)
            length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cycle = length // 50
            count = 0
            while True:
                for x in range(cycle):
                    success, frame = cap.read()
                if not success: break
                frame = cv2.resize(frame, (224, 224))
                filename = f"{self.source_folder_images}/{video_count}_{count:03d}.png"
                cv2.imwrite(filename, frame)
                count += 1
            cap.release()
            destination = self.video_folder_done
            print("Load videos:", source, destination)
            shutil.move(source, destination)
            video_count += 1
        self.load_images()

    def load_images(self):
        make(self.source_folder_images)
        image_names = os.listdir(self.source_folder_images)
        for number in range(len(image_names)):
            self.images.append(OwnImage(number, self, image_names))

    def load_runs(self):
        runs = db_read_model_run_log(self)
        for run in runs:
            self.runs.append(Run(self, run))

    def reload_images(self):
        self.images = []
        self.load_images()

    def get_image(self, number):
        result = next((x for x in self.images if x.number == number), None)
        return result

    def get_image_name(self, name):
        result = next((x for x in self.images if x.name == name), None)
        return result

    def get_run(self, number):
        result = next((x for x in self.runs if x.number == number), None)
        return result

    def get_next_image(self, image):
        if image.number >= len(self.images):
            return image
        else:
            return self.get_image(image.number + 1)

    def get_prev_image(self, image):
        if image.number <= 0:
            return image
        else:
            return self.get_image(image.number - 1)

    def initiate_labels(self):
        path = self.list_of_labels_path
        if not os.path.exists(path):
            print(f"No labels file for:{self}. Creating one")
            MyLabel(name="Label", model=self, colour="white", width=30, height=40)
            return

        f = open(path, "r")
        for line in f:
            result = line.strip().split()
            # print(f"Load labels for {self}: {result}")
            if len(result) == 5:
                number, colour, name, w, h = result
            else:
                continue
            MyLabel(name=name, model=self, colour=colour, width=int(w), height=int(h), external_update=False)

    def label_names(self):
        names = []
        for label in self.labels: names.append(label.name)
        return names

    def get_label(self, number):
        if len(self.labels) == 0: return MyLabel(model=self, name="Label", colour="white", width=30, height=40)
        result = next((x for x in self.labels if x.number == number), None)
        if not result: result = self.labels[0]
        return result

    def write_labels_to_file(self):
        if not os.path.exists(self.source_folder_labels):
            os.makedirs(self.source_folder_labels)

        f = open(self.list_of_labels_path, "w")
        f.truncate(0)
        for label in self.labels:
            string = f"{label.number} {label.colour} {label.name} {label.width} {label.height}"
            f.write(f"{string}\n")
        f.close()

    def create_yaml(self):
        # make(self.yaml_path)
        f = open(self.yaml_path, "w")
        f.truncate(0)
        line1 = f"train: {settings.home_string}/{self.model_folder}"
        line2 = f"val: {settings.home_string}/{self.model_folder}"
        line3 = f"nc: {len(self.labels)}"
        line4 = f"names: {self.label_names()}"
        for x in [line1, line2, line3, line4]:
            f.write(f"{x}\n")

    def set_up_data(self):
        make(self.model_folder)
        make(self.model_folder_images)
        make(self.model_folder_labels)
        delete_files(self.model_folder_images)
        delete_files(self.model_folder_labels)
        for image in self.images:
            if image.include_in_training():
                shutil.copy(image.image_path, self.model_folder_images)
        for filename in os.listdir(self.source_folder_labels):
            source = self.source_folder_labels + "/" + filename
            shutil.copy(source, self.model_folder_labels)

    def train(self):
        start_time = now()
        print("Start:", start_time)
        self.set_up_data()
        self.create_yaml()
        letter = self.size[0]
        yolo_model = YOLO(f"yolov8{letter}.pt")
        # for x in range(15):
        #     yolo_model.layers[x].trainable = False
        yolo_model.train(data=f"{self.yaml_path}", batch=2, imgsz=640, epochs=self.epochs, workers=0, patience=200)
        self.save_boxes()
        time = now() - start_time
        time = round(time.seconds / 60, 2)
        self.save_model(time)

        print("End:", now())
        print("Train time:", self.time)

    def save_model(self, time):
        directory = "runs/detect/"
        subdirectories = os.listdir(directory)
        max = 0
        for dir in subdirectories:
            if len(dir) > 5 and int(dir[5:]) > max: max = int(dir[5:])
        source_model = directory + "train" + str(max) + "/weights/" + "best.pt"
        source_csv = directory + "train" + str(max) + "/results.csv"
        destination = self.model_path
        shutil.copy(source_model, destination)
        print(f"Saved {source_model} to {destination}")
        map50, map95 = self.get_map(source_csv)
        self.save_map(map50, map95)
        self.save_time(time)

        db_write_model_run_log(self.name, now(), max, self.size, self.epochs, time, map50, map95)

    def get_map(self, source):
        final_line = open(source).readlines()[-1].split(",")
        map50 = final_line[6].strip()
        map95 = final_line[7].strip()
        return map50, map95

    def time_f(self):
        if self.time:
            time = "%.1f" % self.time
            return f"{time} min"
        else:
            return ""

    def map50_f(self):
        return map_format(self.map50)

    def map95_f(self):
        return f"{round(float(self.map95), 3) * 100}%"

    def save_name(self, value):
        self.name = value
        write_models_to_file()

    def save_size(self, value):
        self.size = value
        db_update(self.name, "size", value, "string")

    def save_epochs(self, value):
        self.epochs = int(value)
        db_update(self.name, "epochs", value, "float")

    def save_threshold(self, value):
        self.threshold = float(value)
        db_update(self.name, "threshold", value, "float")
        self.delete_boxes()

    def save_time(self, value):
        self.time = value
        db_update(self.name, "time", value, "float")

    def save_map(self, map50, map95):
        db_update(self.name, "map50", map50, "float")
        db_update(self.name, "map95", map95, "float")

    def delete_boxes(self):
        print("Saving boxes:", self, self.boxes_path)
        f = open(self.boxes_path, "w")
        f.truncate(0)
        f.close()

    def save_boxes(self):
        f = open(self.boxes_path, "w")
        self.delete_boxes()
        for image in self.images:
            image.box_list = []
            self.boxes(image)
            for id, x1, y1, x2, y2 in image.box_list:
                line = f"{image.name}, {id}, {x1}, {y1}, {x2}, {y2}"
                f.write(f"{line}\n")
        f.close()

    def get_next_save_file(self, prefix):
        files = os.listdir(self.source_folder_images)
        max = -1
        for file in files:
            if file[0] == prefix:
                result = file[2:-4]
                result = int(result)
                if result > max: max = result
                try:
                    result = int(result)
                    if result > max: max = result
                except:
                    pass
        return f"{self.source_folder_images}/{prefix}_{max + 1}.png"

    def exists(self):
        return os.path.exists(self.model_path)

    def load_boxes(self):
        if not os.path.exists(self.boxes_path): return

        f = open(self.boxes_path, "r")
        for line in f:
            line = line.strip()

            image_name, id, x1, y1, x2, y2 = line.split(",")
            image = self.get_image_name(image_name)
            # print(image, image_number, id, x1, y1, x2, y2)
            if image:
                image.box_list.append((int(id), int(x1), int(y1), int(x2), int(y2)))

    def boxes(self, image):
        if not self.exists(): return []
        if len(self.images) == 0: return []
        if image is None: return []
        # print("Boxes:", self.images)
        if len(image.box_list) > 0:
            return image.box_list
        # print("Boxes", image)
        model = YOLO(self.model_path)
        result = model(image.image_cv2)[0].boxes
        boxes = result.xyxy.cpu().numpy()
        confidences = result.conf.cpu().numpy()
        class_ids = result.cls.cpu().numpy().astype(int)
        image.box_list = []
        for box, confidence, class_id in zip(boxes, confidences, class_ids):
            if confidence > self.threshold:
                x1, y1, x2, y2 = integers(box)
                w, h = x2 - x1, y2 - y1
                image.box_list.append((class_id, x1 + w // 2, y1 + h // 2, x2 + w // 2, y2 + h // 2))
        return image.box_list

    def boxes_live(self, image):
        model = YOLO(self.model_path)
        result = model(image)[0].boxes

        boxes = result.xyxy.cpu().numpy()
        confidences = result.conf.cpu().numpy()
        class_ids = result.cls.cpu().numpy().astype(int)
        box_list = []
        for box, confidence, class_id in zip(boxes, confidences, class_ids):
            if confidence > 0.50:
                x1, y1, x2, y2 = integers(box)
                w, h = x2 - x1, y2 - y1
                box_list.append((class_id, x1 + w // 2, y1 + h // 2, x2 + w // 2, y2 + h // 2))
        return box_list

    # def boxes(self, image):
    #     return []

def make(path):
    if not os.path.exists(path):
        print("Make directory:", path)
        os.makedirs(path)

def write_models_to_file():
    f = open(settings.list_of_models_path, "w")
    f.truncate(0)
    for model in models:
        string = str(model)
        print(string)
        f.write(f"{string}\n")
    f.close()

def load_models():
    if not os.path.exists(settings.list_of_models_path):
        Model(name="Model")
        return

    f = open(settings.list_of_models_path, "r")
    for line in f:
        name = line.strip()
        Model(name=name, initial_setup=False)

def get_model(number):
    if len(models) == 0: return Model(name="Model")
    result = next((x for x in models if x.number == number), None)
    if not result: result = models[0]
    return result

def delete_model(model):
    model.delete_folders()
    models.remove(model)
    write_models_to_file()

# for model in models:
#     print(model.image_directory)
#     print(model.label_directory)

# image_names = os.listdir(models[0].image_directory)
