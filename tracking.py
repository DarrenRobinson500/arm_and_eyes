'''
To do
 - Box and track objects from 1 camera - Done
 - Box and track objects from 2 cameras - Done
 - Box and track objects from 1 camera (using same approach as w_cam) - Done
 - Set up new tkinter
 - Integrate in w_cam
'''


from ultralytics import YOLO
import cv2
import threading
from camera import Camera
from model import integers
from utilities import *

def camera_thread(cam, model):
    print(f"Starting camera {cam.number}")
    for results in model.track(source=cam.number, show=False, stream=True, persist=True, verbose=False):
        frame = results.orig_img
        boxes = get_boxes(results.boxes)
        for class_id, x1, y1, x2, y2, tracker_id in boxes:
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
            cv2.putText(frame, str(tracker_id), (x1 + 10, y1 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow(f"Viewer {cam.number}", frame)
        if cv2.waitKey(500) == 27: break

def start_cam_threads(cam_1, cam_2):
    print("Starting cam threads")
    model_1, model_2 = YOLO("models/Arm/Arm.pt"), YOLO("models/Arm/Arm.pt")
    # cam_1, cam_2 = Camera(0), Camera(2)
    thread1 = threading.Thread(target=camera_thread, args=(cam_1, model_1), daemon=True)
    thread2 = threading.Thread(target=camera_thread, args=(cam_2, model_2), daemon=True)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

# start_threads()





# def single_camera():
#     box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.5)
#     for result in model_1.track(source=0, show=False, stream=True, verbose=False):
#         frame = result.orig_img
#         detections = sv.Detections.from_yolov8(result)
#         detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
#         labels = [f"#{tracker_id} {model.model.names[class_id]} {confidence:0.2f}" for a, b, confidence, class_id, tracker_id in detections]
#         frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
#         cv2.imshow("Viewer", frame)
#         if cv2.waitKey(500) == 27: break

# class CameraWithTracking:
#     def __init__(self, number):
#         self.number = number
#         self.vid = cv2.VideoCapture(number)
#         # print(dir(self.vid))
#         self.name = f"Camera_{number}"
#         self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
#         self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
#         self.labels = []
#         self.canvas = None
#         cameras.append(self)
#
#     def __str__(self):
#         return f"{self.number} {self.name}"
#
#     def get_frame(self):
#         is_open, frame = self.vid.read()
#         if is_open:
#             return is_open, frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#     def get_frame_new(self, model, record=False):
#         result = model.track(source=self.number, show=False, stream=True, persist=True, verbose=False)
#         frame_cv = result.orig_img
#         frame = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
#         cv2.imshow(self.name + " A", frame_cv)

        # return frame_cv, frame


# def dual_cam():
#     cam_1 = CameraWithTracking(0)
#     cam_2 = CameraWithTracking(2)
#
#     continue_loop = True
#     while continue_loop:
#         for cam in [cam_1,]:
#             result = cam.get_frame(model)
#             if result:
#                 is_open, frame_cv, frame = result
#                 # cv2.imshow(cam.name, frame_cv)
#         if cv2.waitKey(30) == 27: continue_loop = False


# def one_frame():
#     for results in model.track(source=0, show=False, stream=True, persist=True, verbose=False):
#         frame = results.orig_img
#         boxes = get_boxes(results.boxes)
#         for class_id, x1, y1, x2, y2, tracker_id in boxes:
#             frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
#             cv2.putText(frame, str(tracker_id), (x1 + 10, y1 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
#         cv2.imshow("Photo", frame)
#         time.sleep(.2)
#         if cv2.waitKey(500) == 27: break





# def run_tracker_in_thread_old(cam, model):
#     cam.box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.5)
#     for result in model.track(source=cam.number, show=False, stream=True, verbose=False):
#         cam.frame = result.orig_img
#         cam.detections = sv.Detections.from_yolov8(result)
#         print(cam.detections)
#
#         if result:
#             try:
#                 cam.detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
#             except:
#                 pass
#         labels = [f"#{tracker_id} {model.model.names[class_id]} {confidence:0.2f}" for _, _, confidence, class_id, tracker_id in cam.detections]
#         frame = cam.box_annotator.annotate(scene=cam.frame, detections=cam.detections, labels=labels)
#
#         cv2.imshow(f"Viewer {cam.number}", frame)
#         if cv2.waitKey(500) == 27: break
#



    #
    #
    # is_open, frame_cv, frame = camera_with_tracking.get_frame()
    # if is_open:
    #     results = model.track(source=frame, persist=True)
    #     res_plotted = results[0].plot()
    #     cv2.imshow('p', res_plotted)
    #     if cv2.waitKey(1) == ord('q'): break



# def start_thread(cam, model):
#     thread = threading.Thread(target=run_tracker_in_thread, args=(cam, model), daemon=True)
#     thread.start()
#     thread.join()




# cam_1.box_annotator = sv.BoxAnnotator(thickness=1, text_thickness=1, text_scale=0.5)

        # detections = sv.Detections.from_yolov8(result)
        # for z in result:
        #     box = z.boxes.xyxy[0]
        #     x1, y1, x2, y2 = box[0].item(), box[1].item(), box[2].item(), box[3].item()
        #     print(x1)
        #     # print(x1, y1, x2, y2)
        #     # print(z.boxes.xyxy)
        #     start_point = (5, 5)
        #     end_point = (22, 22)
        #     color = (255, 0, 0)
        #     thickness = 2
        #     frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        #
        #     # frame = cv2.rectangle(frame, (10, 10), (50, 50), "blue", 1)
        #     cv2.imshow("Photo", frame)
        # break

# single_camera()
# one_frame()

# cv2.destroyAllWindows()

# dual_cam()






