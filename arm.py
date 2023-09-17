from arduino_2 import *
import time

class Arm:
    def __init__(self):
        self.connect()
        self.move(450, -100, 55)

    def connect(self):
        get_port()
        print("Waiting for homing")
        wait_for_homing()

    def move(self, x, y, z):
        print("Running command", x, y, z)
        result = get_angles(x, y, z)
        command(result_to_text(result))

    def move_angle(self, a0, a1, a2):
        result = f"p {a0} {a1} {a2}"
        command(result)



    def calibrate(self, app, x_min, x_max, y_min, y_max, z_min, z_max):
        print("Calibrate:", x_min, x_max, y_min, y_max, z_min, z_max)

        for z in [z_min, z_max]:
            for x in [x_min, x_max]:
                for y in [y_min, y_max]:
                    print(f"x: {x} [{x_min}, {x_max}]")
                    print(f"y: {y} [{y_min}, {y_max}]")
                    print(f"z: {z} [{z_min}, {z_max}]")
                    # print("Running command", x, y, z)
                    self.move(x, y, z)
                    result = app.get_head_coords()
                    if result:
                        x1, y1, x2, y2 = result
                        data = x1, y1, x2, y2, x, y, z
                        result = app.scene.new_calibration_point(data)
                        app.model_active = result
                    else:
                        print("Didn't create calibration point")
                        app.capture_image()
