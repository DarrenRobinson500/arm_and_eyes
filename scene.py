import numpy as np
from sklearn.linear_model import LinearRegression
from settings import *
from sql import *

scenes = []

def rounded(vars):
    result = []
    for var in vars:
        result.append(round(var, 1))
    return result

class Point:
    def __init__(self, data):
        print(data)
        self.data = data
        self.x1, self.y1, self.x2, self.y2, self.x, self.y, self.z = data
        print("Created point:", self.data)

class CalibrationPoint:
    def __init__(self, scene, data):
        self.number = len(scene.calibration_points)
        self.scene = scene
        self.data = data
        self.x1, self.y1, self.x2, self.y2, self.x, self.y, self.z = data
        self.error = -1
        self.data_and_error = list(self.data)
        self.data_and_error.append(self.error)
        self.values = self.data_and_error

    def __str__(self):
        return str(self.data_and_error)

    def calc_error(self):
        if not self.scene.model_x:
            print("Determining error - prediction model not created yet")
            return
        pred_x, pred_y, pred_z = self.scene.pos(self.x1, self.y1, self.x2, self.y2)
        self.error = (pred_x - self.x) * (pred_x - self.x) + (pred_y - self.y) * (pred_y - self.y) + (pred_z - self.z) * (pred_z - self.z)
        self.data_and_error[-1] = self.error
        # print("Error calc:", self, self.error)


class Scene:
    def __init__(self, name, initial_setup=True):
        self.number = len(scenes)
        self.name = name
        # print("New scene:", self.name)
        self.calibration_points = []
        self.model_x = None
        self.model_y = None
        self.model_z = None
        scenes.append(self)
        self.load_calibration_points()
        self.calibrate()
        # self.print_calibration_points()
        if initial_setup:
            db_write_scenes(self.name)

    def __str__(self):
        return self.name

    def new_calibration_point(self, data):
        new = CalibrationPoint(self, data)
        self.calibration_points.append(new)
        db_write_calibration_point(self.name, data)
        self.calibrate()
        print("New calibration point. Total number of calibration points:", len(self.calibration_points))
        return len(self.calibration_points) >= 4

    def load_calibration_points(self):
        points = db_read_calibration_points(self.name)
        for data in points:
            new = CalibrationPoint(self, data[1:])
            self.calibration_points.append(new)

    def print_calibration_points(self):
        print("\nCalibration Points for:", self)
        for point in self.calibration_points:
            print(point)

    def calc_errors(self):
        for point in self.calibration_points: point.calc_error()

    def get_model_inputs(self, x1, y1, x2, y2):
        self.d = 100
        d = self.d
        return x1, y1, x2, y2, x1 / (x2 + d), x1 / (y2 + d), y1 / (x2 + d), y1 / (y2 + d), x2 / (x1 + d), x2 / (y1 + d), y2 / (x1 + d), y2 / (y1 + d)

    def calibrate(self):
        if len(self.calibration_points) < 4:
            print("Not calibrating: Insufficient calibration points")
            return
        global model_x, model_y, model_z
        pos_i, pos_x, pos_y, pos_z = [], [], [], []

        for point in self.calibration_points:
            x1, y1, x2, y2, x, y, z = point.data

            inputs = self.get_model_inputs(x1, y1, x2, y2)
            pos_i.append((inputs))
            pos_x.append(x)
            pos_y.append(y)
            pos_z.append(z)
        pos_i = np.array(pos_i)
        pos_x = np.array(pos_x)
        pos_y = np.array(pos_y)
        pos_z = np.array(pos_z)

        self.model_x = LinearRegression().fit(pos_i, pos_x)
        self.model_y = LinearRegression().fit(pos_i, pos_y)
        self.model_z = LinearRegression().fit(pos_i, pos_z)

        self.calc_errors()

    def pos(self, x1, y1, x2, y2):
        input = self.get_model_inputs(x1, y1, x2, y2)
        input = np.array(input).reshape(1, -1)
        # print(input)
        x = int(self.model_x.predict(input)[0])
        y = int(self.model_y.predict(input)[0])
        z = int(self.model_z.predict(input)[0])

        x, y, z = rounded([x, y, z])

        # print(f"({x1}, {y1}, {x2}, {y2}) => ({x}, {y}, {z})")

        return x, y, z

def load_scenes():
    scenes = db_read_scenes()
    for scene in scenes:
        new_scene = Scene(name=scene[0], initial_setup=False)
        # new_scene.print_calibration_points()

def get_scene(number):
    if len(scenes) == 0: return Scene(name="Scene")
    result = next((x for x in scenes if x.number == number), None)
    if not result: result = scenes[0]
    return result

load_scenes()

scene_A = get_scene(0)
