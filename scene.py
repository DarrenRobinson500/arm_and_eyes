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
        if initial_setup:
            db_write_scenes(self.name)

    def load_calibration_points(self):
        points = db_read_calibration_points(self.name)
        for scene, x1, y1, x2, y2, x, y, z in points:
            self.calibration_points.append((x1, y1, x2, y2, x, y, z))

    def new_calibration_point(self, x1, y1, x2, y2, x, y, z):
        self.calibration_points.append((x1, y1, x2, y2, x, y, z))
        db_write_calibration_point(self.name, x1, y1, x2, y2, x, y, z)
        self.calibrate()

    def get_model_inputs(self, x1, y1, x2, y2):
        d = 100
        return x1, y1, x2, y2, x1 / (x2 + d), x1 / (y2 + d), y1 / (x2 + d), y1 / (y2 + d), x2 / (x1 + d), x2 / (y1 + d), y2 / (x1 + d), y2 / (y1 + d)

    def calibrate(self):
        global model_x, model_y, model_z
        pos_i, pos_x, pos_y, pos_z = [], [], [], []

        for x1, y1, x2, y2, x, y, z in self.calibration_points:
            inputs = self.get_model_inputs(x1, y1, x2, y2)
            print((x, y, z), "=>", (x1, y1, x2, y2))
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

    def pos(self, x1, y1, x2, y2):
        input = self.get_model_inputs(x1, y1, x2, y2)
        input = np.array(input).reshape(1, -1)
        x = model_x.predict(input)[0]
        y = model_y.predict(input)[0]
        z = model_z.predict(input)[0]

        x, y, z = rounded([x, y, z])

        print(f"({x1}, {y1}, {x2}, {y2}), => ({x}, {y}, {z})")

        return x, y, z

def load_scenes():
    scenes = db_read_scenes()
    for scene in scenes:
        Scene(name=scene[0], initial_setup=False)

def get_scene(number):
    if len(scenes) == 0: return Scene(name="Scene")
    result = next((x for x in scenes if x.number == number), None)
    if not result: result = scenes[0]
    return result

load_scenes()