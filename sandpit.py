from sql import *
from datetime import datetime, timedelta
now = datetime.now

# def db_write_model_run_log(model, date, run, epochs, time, map50, map95, folder):

# date = now()
# db_write_model_run_log("Ball", date, 15, "large", 200, 5.3, 0.9, 0.7)
#
# result = db_read_model_run_log("Ball")
# print(result)
#
# n = 0.2221112
# print("%.3f" % n)


# start = now() - timedelta(seconds=380)
# end = now()
# time = end - start
# print(round(time.seconds / 60,2))
# time = round((now() - start_time).seconds / 60, 2)

# boxes0 = [(0, 20, 21), (0, 10, 11), (0, 50, 41)]
# boxes1 = [(0, 30, 31), (0, 40, 41)]
#
# boxes0 = sorted(boxes0, key=lambda x: x[1])
# boxes1 = sorted(boxes1, key=lambda x: x[1])
#
# boxes = []
# for box0, box1 in zip(boxes0, boxes1):
#     class0, x0, y0 = box0
#     class1, x1, y1 = box1
#     boxes.append((class0, x0, y0, x1, y1))
#
# print(boxes)



def get_box_centers(boxes):
    result = []
    for box in boxes:
        class_id, x1, y1, x2, y2 = box
        result.append((class_id, (x1 + x2) // 2, (y1 + y2) // 2))
    return result


boxes0 = [(0, 20, 21, 30, 31), (0, 10, 11, 20, 21), (0, 50, 41, 60, 51)]
boxes0 = get_box_centers(boxes0)
print(boxes0)