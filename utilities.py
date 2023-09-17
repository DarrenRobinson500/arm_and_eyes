from tkinter import *
import ttkbootstrap as ttk
import threading
# from tkinter import *
import cv2
from PIL import Image, ImageTk
from PIL import Image, ImageTk

items = []

class Item_Test:
    def __init__(self, values):
        self.label, self.i1, self.x1, self.y1, self.i2, self.x2, self.y2 = values
        self.number = len(items)
        print("New item:", str(self))
        items.append(self)

    def __str__(self):
        return f"Item {self.number}: {self.label} {self.i1} {self.x1} {self.y1} {self.i2} {self.x2} {self.y2}"

values = [2, 4, 10, 10, 3, 20, 20]

Item_Test(values)

trees = []

# -------------------
# ----- Numbers -----
# -------------------

def integers(list):
    new_list = []
    for item in list: new_list.append(int(item))
    return new_list

# -------------------
# ----- Boxes -----
# -------------------

def get_boxes(result):
    try:
        boxes = result.xyxy.cpu().numpy()
        confidences = result.conf.cpu().numpy()
        class_ids = result.cls.cpu().numpy().astype(int)
        tracker_ids = result.id.cpu().numpy().astype(int)
        box_list = []
        for box, confidence, class_id, tracker_id in zip(boxes, confidences, class_ids, tracker_ids):
            if confidence > 0.50:
                x1, y1, x2, y2 = integers(box)
                w, h = x2 - x1, y2 - y1
                box_list.append((class_id, x1 + w // 2, y1 + h // 2, x2 + w // 2, y2 + h // 2, tracker_id))
        return box_list
    except:
        return []

def get_box_centers(boxes):
    result = [] # class, i, x, y
    if boxes:
        for box in boxes:
            # These are boxes from 1 camera. x1 and x2 are the outer boundaries of a single image
            # i = tracker id
            label, x1, y1, x2, y2, i = box
            output = (label, i, (x1 + x2) // 2, (y1 + y2) // 2)
            result.append(output)
        return result

def combine_boxes(boxes_1, boxes_2):
    if not boxes_1 or not boxes_2: return
    boxes_output = []
    boxes_1_existing = None
    boxes_2_existing = None

    # Get the centers of the boxes
    boxes_1 = get_box_centers(boxes_1)
    boxes_2 = get_box_centers(boxes_2)

    # Separate out the known items
    for item in items:
        boxes_1_existing = [box for box in boxes_1 if box[1] == item.i1]
        boxes_2_existing = [box for box in boxes_2 if box[1] == item.i2]
        boxes_1 = [box for box in boxes_1 if box[1] != item.i1]
        boxes_2 = [box for box in boxes_2 if box[1] != item.i2]

    # Create the set of ids
    label_set = {box[0] for box in boxes_1} | {box[0] for box in boxes_2}

    # Combine the existing boxes and update the respective items x1, y1, x2, y2
    print("\nBoxes 1 existing:", boxes_1_existing)
    print("Boxes 2 existing:", boxes_2_existing)
    if boxes_1_existing and boxes_2_existing:
        for item in items:
            output_1 = [(box[2], box[3]) for box in boxes_1_existing if box[1] == item.i1]
            output_2 = [(box[2], box[3]) for box in boxes_2_existing if box[1] == item.i2]
            try:
                item.x1, item.y1 = output_1[0]
                item.x2, item.y2 = output_2[0]
            except:
                pass
            print("Output 1:", output_1)
            print("Output 2:", output_2)

    # Loop through each label
    for label in label_set:
        print("\nLabel:", label)
        boxes_1_temp = [box for box in boxes_1 if box[0] == label]
        print("Boxes_1:", boxes_1_temp)
        boxes_2_temp = [box for box in boxes_2 if box[0] == label]
        print("Boxes_2:", boxes_2_temp)

        # Sort them across the x axis
        boxes_1_temp = sorted(boxes_1_temp, key=lambda x: x[2])
        boxes_2_temp = sorted(boxes_2_temp, key=lambda x: x[2])
        print("Boxes_1 (sorted):", boxes_1_temp)
        print("Boxes_2 (sorted):", boxes_1_temp)

        # Combine the new boxes and add them to output
        for box_1, box_2 in zip(boxes_1_temp, boxes_2_temp):
            label_1, i1, x1, y1 = box_1
            label_2, i2, x2, y2 = box_2
            box_output = [label_1, i1, x1, y1, i2, x2, y2]
            Item_Test(box_output)
            print("New output (single):", box_output)
            boxes_output.append(box_output)

    return boxes_output

boxes_1 = [
    [1, 10, 20, 30, 40, 1],
    [1, 20, 30, 40, 50, 2],
    [2, 110, 120, 130, 140, 3],
    [2, 120, 130, 140, 150, 4],
]

boxes_2 = [
    [1, 210, 220, 230, 240, 1],
    [1, 190, 230, 240, 250, 2],
    [2, 310, 320, 330, 340, 3],
]


print("Final output:", combine_boxes(boxes_1, boxes_2))
# for item in items: print(item)

print([str(item) for item in items])

def combine_boxes_simple(boxes1, boxes2):
    if not boxes1 or not boxes2: return
    # Get the centers of the boxes
    boxes1 = get_box_centers(boxes1)
    boxes2 = get_box_centers(boxes2)
    # Sort them across the x axis
    boxes1 = sorted(boxes1, key=lambda x: x[2])
    boxes2 = sorted(boxes2, key=lambda x: x[2])

    # Combine them
    boxes = []
    for box1, box2 in zip(boxes1, boxes2):
        label_1, i1, x1, y1 = box1
        label_2, i2, x2, y2 = box2
        boxes.append([label_1, i1, x1, y1, i2, x2, y2])

    return boxes


# -------------------
# ----- Tkinter -----
# -------------------

def button_row(buttons, frame):
    for text, command in buttons:
        new_button = ttk.Button(frame, text=text, command=command, width=15)
        new_button.pack(side="left", padx=5, pady=5)

def write(widget, text):
    widget.delete(0, END)
    widget.insert(0, text)

def new_entry_box(frame, initial_value, row, column):
    variable = StringVar(frame)
    e_model_name = Entry(frame, textvariable=variable)
    e_model_name.grid(row=row, column=column)
    variable.set(initial_value)
    return variable

def new_tree(heading, frame, height, width, command_if_changed, side="top"):
    ttk.Label(frame, text=heading, style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
    f_tree = Frame(frame)
    f_tree.pack(pady=10, padx=10, anchor=NW)
    s_tree = Scrollbar(f_tree)
    s_tree.pack(side=RIGHT, fill=Y)
    tree = ttk.Treeview(f_tree, height=height, yscrollcommand=s_tree.set, selectmode="extended")
    s_tree.config(command=tree.yview)
    tree['columns'] = ("Name")
    tree.column("#0", width=0, minwidth=0)
    tree.column("Name", anchor=W, width=width)
    tree.heading("#0", text="")
    tree.heading("Name", text=heading, anchor=W)
    tree.pack(side=side)
    tree.tag_configure("oddrow", background="white")
    tree.tag_configure("evenrow", background="lightblue")
    tree.bind('<<TreeviewSelect>>', command_if_changed)
    trees.append(tree)
    return tree

def new_tree_complex(frame, heading, height, columns, widths, command_if_changed=None, command_if_selected=None, side="top"):
    # print("Making new tree:", heading, height)
    # ttk.Label(frame, text=heading, style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
    f_tree = Frame(frame)
    f_tree.pack(pady=10, padx=10, anchor=NW)
    s_tree = Scrollbar(f_tree)
    s_tree.pack(side=RIGHT, fill=Y)
    
    tree = ttk.Treeview(f_tree, height=height, yscrollcommand=s_tree.set, selectmode="extended")
    s_tree.config(command=tree.yview)
    tree['columns'] = columns
    tree.column("#0", width=0, minwidth=0)
    tree.heading("#0", text="")
    for name, width in zip(columns, widths):
        tree.column(name, anchor=W, width=width)
        tree.heading(name, text=name, anchor=W)
    tree.pack(side=side, anchor=NW)
    if command_if_changed: tree.bind('<<TreeviewSelect>>', command_if_changed)
    if command_if_selected: tree.bind('<ButtonRelease-1>', command_if_selected)
    tree.tag_configure("red", background="red")
    tree.tag_configure("blue", background="blue")
    return tree

def get_number(x):
    if len(x) == 0:
        return 0
    else:
        return int(x[0])

def map_format(x):
    return "%.3f" % x

def time_format(x):
    if x:
        x = "%.1f" % x
        return f"{x} min"
    else:
        return ""

def clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)



