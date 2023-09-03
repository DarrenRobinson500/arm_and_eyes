import ttkbootstrap as ttk
import tkinter
from tkinter import *
import cv2
from PIL import Image, ImageTk
from PIL import Image, ImageTk


trees = []

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

def new_tree_complex(frame, heading, height, columns, widths, command_if_changed=None, side="top"):
    # print("Making new tree:", heading, height)
    ttk.Label(frame, text=heading, style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
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

def get_box_centers(boxes):
    result = []
    for box in boxes:
        class_id, x1, y1, x2, y2 = box
        result.append((class_id, (x1 + x2) // 2, (y1 + y2) // 2))
    return result


