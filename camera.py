from utilities import *

cameras = []

class Camera_minimal:
    def __init__(self, number):
        self.number = number
        self.name = f"Camera_{number}"
        cameras.append(self)

class Camera:
    def __init__(self, number):
        self.number = number
        self.vid = cv2.VideoCapture(number)
        # print(dir(self.vid))
        self.name = f"Camera_{number}"
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.labels = []
        self.canvas = None

        # Tracking variables
        self.box_annotator = None
        self.frame = None
        self.detections = None

        cameras.append(self)

    def __str__(self):
        return f"{self.number} {self.name}"
    def get_frame(self, model, record=False):
        is_open, frame = self.vid.read()
        if is_open:
            if record:
                filename = model.get_next_save_file()
                print("Recording:", record, filename)
                cv2.imwrite(filename, frame)

            return is_open, frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def set_canvas(self, canvas):
        self.canvas = canvas

    def __del__(self):
        self.vid.release()

def get_cam(number):
    if len(cameras) == 0: return Camera(number=0)
    result = next((x for x in cameras if x.number == number), None)
    if not result: result = cameras[0]
    return result

Camera(0)
Camera(1)
Camera(2)

# for cam in cameras: print(cam)

