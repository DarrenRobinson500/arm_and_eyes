from sql import *
from utilities import *

class Run:
    def __init__(self, model, run_details):
        self.number = len(model.runs)
        self.model = model
        model, date, run, size, epochs, time, map50, map95, folder = run_details
        self.date = date
        self.run = run
        self.size = size
        self.epochs = epochs
        self.time = time
        self.map50 = map50
        self.map95 = map95
        self.folder = folder

    def __str__(self):
        result = f"Model: {self.model} Date: {self.date} Run: {self.run} Map50: {self.map50}"
        return result

