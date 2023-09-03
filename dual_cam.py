from tkinter import *
import cv2

cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(2)

while True:
    ret, frame0 = cap0.read()
    if ret:
        cv2.imshow("Frame 0", frame0)

    ret, frame1 = cap1.read()
    if ret:
        cv2.imshow("Frame 1", frame1)

    ret, frame2 = cap2.read()
    if ret:
        cv2.imshow("Frame 2", frame2)

    if cv2.waitKey(1) in [32, ]: break

cap0.release()
cap1.release()
cv2.destroyAllWindows()