from camera import *
from time import sleep
from datetime import *
from item import *
from model import *
from scene import *
from arm import Arm
from excel import add_model_to_excel, add_points_to_excel

class App:
    def __init__(self, arm_active=True, eyes_active=True):
        # Window setup
        self.name = "Viewer"
        self.window = ttk.Window(themename='litera')
        self.window.title(self.name)
        self.window.geometry("2020x1000+0+0")
        self.thread_delay = 3

        # Model and Scene
        load_models()
        self.model = models[0]
        self.scene = scenes[0]
        self.model_active = (len(self.scene.calibration_points) >= 4)

        # Sandpit

        # Variables
        self.move_to_selected_object = True
        self.set_up_variables()
        self.items = []
        self.item_selected_time = datetime.now()
        self.excel_column = 16

        # Frames
        self.set_up_frames(frame=self.window)
        self.set_up_control_frame(frame=self.frame_control)
        self.set_up_calibration_frame(frame=self.frame_right)
        self.set_up_log_frame(frame=self.frame_right)
        self.set_up_keys()

        # Cameras
        self.eyes_active = eyes_active
        if self.eyes_active:
            self.set_up_cameras(frame=self.frame_cam, cam_no_1=0, cam_no_2=1)

        # Arm
        self.arm_active = arm_active
        if self.arm_active:
            self.arm = Arm()

        # Start threads
        if self.eyes_active:
            self.start_threads(cam_1=self.cam_1, cam_2=self.cam_2)

        # Main loop
        self.window.mainloop()

    # ----------------------
    # ---- VARIABLES -------
    # ----------------------

    def set_up_variables(self):
        print("Set up variables")
        self.object, self.v_i1, self.v_x1, self.v_y1, self.v_i2, self.v_x2, self.v_y2, self.v_x, self.v_y, self.v_z = StringVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()
        self.selected_object_variables = [self.object, self.v_i1, self.v_x1, self.v_y1, self.v_i2, self.v_x2, self.v_y2, self.v_x, self.v_y, self.v_z]
        self.v_x_min, self.v_x_max, self.v_y_min, self.v_y_max, self.v_z_min, self.v_z_max = IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()
        self.calibration_variables = [self.v_x_min, self.v_x_max, self.v_y_min, self.v_y_max, self.v_z_min, self.v_z_max]

    # -------------------
    # ---- FRAMES -------
    # -------------------

    def set_up_frames(self, frame):
        print("Set up frames")
        self.frame_left = Frame(frame, width=100, height=800)
        self.frame_centre = Frame(frame, width=1400, height=800)
        self.frame_right = Frame(frame, width=400, height=800)

        self.frame_cam = Frame(self.frame_centre, width=800, height=800)
        self.frame_control = Frame(self.frame_centre, width=800, height=800)

        frames = [self.frame_left, self.frame_centre, self.frame_right]
        for frame in frames:
            frame.pack(side="left", anchor=NW)

        frames = [self.frame_cam, self.frame_control]
        for frame in frames:
            frame.pack(anchor=NW)

    def set_up_control_frame(self, frame):
        print("Set up control frame")
        # Items Tree
        own_frame = Frame(frame)
        own_frame.pack(anchor=NW, padx=10)
        heading_frame = Frame(own_frame)
        heading_frame.pack(anchor=NW, padx=10)
        ttk.Label(heading_frame, text="Items", style="primary", font=('Helvetica', 12)).pack(anchor=NW, side=LEFT, padx=10, pady=10)
        self.item_function = StringVar()
        self.item_function.set("Move Arm To Item")
        OptionMenu(heading_frame, self.item_function, "Move Arm To Item", "Send to Excel").pack(side=LEFT, padx=10, pady=10)
        self.t_items = new_tree_complex(
            frame=own_frame, heading="Items", height=7, columns=("Item", "i1", "x1", "y1", "i2", "x2", "y2", "x", "y", "z"), widths=(60, 40, 40, 40, 40, 40, 40, 40, 40, 40),
            command_if_selected=self.identified_object_selected)

        # Selected item
        own_frame = Frame(frame)
        own_frame.pack(anchor=NW, padx=10)
        for count, x in enumerate(("Object", "i1", "x1", "y1", "i2", "x2", "y2", "x", "y", "z")):
            Label(own_frame, text=x).grid(row=0, column=count)
            Label(own_frame, textvariable=self.selected_object_variables[count], width=6).grid(row=1, column=count)

    def set_up_calibration_frame(self, frame):
        print("Set up calibration frame")
        ttk.Label(frame, text="Calibration", style="primary", font=('Helvetica', 12)).pack(anchor=NW, padx=10, pady=10)
        self.t_calibration_points = new_tree_complex(
            frame=frame, heading="Calibration Points", height=10, columns=("x1", "y1", "x2", "y2", "x", "y", "z", "Err"), widths=(50, 50, 50, 50, 50, 50, 50, 50))
        self.update_tree(self.t_calibration_points, self.scene.calibration_points)
        own_frame = Frame(frame)
        own_frame.pack(pady=5, anchor=NW)
        Button(own_frame, text="Re-calibrate", command=self.start_calibration_thread).pack(anchor=NW, side=LEFT, padx=10, pady=10)
        Button(own_frame, text="Capture Image", command=self.start_capture_image_thread).pack(side=LEFT, padx=10, pady=10)
        Button(own_frame, text="Model to xlsx", command=self.model_to_xlsx).pack(anchor=NW, pady=10)
        self.add_calibration_min_max(frame)

    def add_calibration_min_max(self, frame):
        print("Set up calibration min max")
        # Heading
        # ttk.Label(frame, text="Calibration Area", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
        # Entry Boxes
        own_frame = Frame(frame)
        own_frame.pack(pady=5, anchor=NW)
        start_values = [400, 500, -50, -150, 30, 80]
        for count, label in enumerate(("x min", "x max", "y min", "y max", "z min", "z max")):
            Label(own_frame, text=label).grid(row=0, column=count)
            new_entry = Entry(own_frame, textvariable=self.calibration_variables[count], width=7, justify='center')
            new_entry.grid(row=1, column=count)
            new_entry.bind("<Key>", self.calibration_entry_box_changed)
            self.calibration_variables[count].set(start_values[count])

        # Buttons
        own_frame = Frame(frame)
        own_frame.pack(pady=5, anchor=NW)
        self.calibration_buttons = []

        b0 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(0), width=10)
        b1 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(1), width=10)
        b2 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(2), width=10)
        b3 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(3), width=10)
        b4 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(4), width=10)
        b5 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(5), width=10)
        b6 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(6), width=10)
        b7 = Button(own_frame, text="XXX", command=lambda: self.run_calibration_button(7), width=10)

        row, column = 1, 1
        for button in [b0, b1, b2, b3, b4, b5, b6, b7]:
            button.grid(row=row, column=column, padx=2, pady=2)
            self.calibration_buttons.append(button)
            column += 1
            if column == 5:
                column = 1
                row += 1

        self.update_calibration_buttons()

    def update_calibration_buttons(self):
        print("Update calibration buttons")
        self.calibration_buttons[0].config(text=f"{self.v_x_min.get()} {self.v_y_min.get()} {self.v_z_min.get()}")
        self.calibration_buttons[1].config(text=f"{self.v_x_max.get()} {self.v_y_min.get()} {self.v_z_min.get()}")
        self.calibration_buttons[2].config(text=f"{self.v_x_min.get()} {self.v_y_max.get()} {self.v_z_min.get()}")
        self.calibration_buttons[3].config(text=f"{self.v_x_max.get()} {self.v_y_max.get()} {self.v_z_min.get()}")
        self.calibration_buttons[4].config(text=f"{self.v_x_min.get()} {self.v_y_min.get()} {self.v_z_max.get()}")
        self.calibration_buttons[5].config(text=f"{self.v_x_max.get()} {self.v_y_min.get()} {self.v_z_max.get()}")
        self.calibration_buttons[6].config(text=f"{self.v_x_min.get()} {self.v_y_max.get()} {self.v_z_max.get()}")
        self.calibration_buttons[7].config(text=f"{self.v_x_max.get()} {self.v_y_max.get()} {self.v_z_max.get()}")

    def set_up_log_frame(self, frame):
        print("Set up log frame")
        ttk.Label(frame, text="Log", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
        own_frame = Frame(frame)
        own_frame.pack(pady=5, anchor=NW)
        text_scroll = Scrollbar(own_frame)
        text_scroll.pack(side=RIGHT, fill=Y)
        self.text = Text(own_frame, width=80, height=10, wrap=WORD, yscrollcommand=text_scroll.set)
        self.text.pack()
        text_scroll.config(command=self.text.yview)

    def add_text(self, text):
        print("Add text")
        self.text.insert(END, str(text) + "\n")
        print("Logging:", text)

    # ------------------------------
    # ----- TREE FUNCTIONALITY -----
    # -----------------------------

    def clear_tree(self, tree):
        print("Clear tree")
        for item in tree.get_children():
            tree.delete(item)

    def update_tree(self, tree, tree_items):
        print("Update tree")
        current_item_number = tree.focus()
        self.clear_tree(tree)
        for item in tree_items:
            # print("Updating tree:", item.number, item.values)
            # print_items(self)
            try:
                tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=item.values)
            except:
                pass
        tree.selection_set(current_item_number)

    # --------------------------
    # ----- TKINTER BASICS -----
    # --------------------------

    def set_up_keys(self):
        print("Set up keys")
        self.window.bind('<Escape>', lambda e: self.exit(e))

    def exit(self, e):
        print("Exit")
        if self.arm_active:
            self.arm.move_angle(0, 0, 0)
        self.window.destroy()


    # --------------------
    # ---- CAMERAS -------
    # --------------------

    def set_up_cameras(self, frame, cam_no_1, cam_no_2):
        print("Set up cameras")
        if not self.eyes_active: return
        self.cam_1 = Camera(number=cam_no_1, frame=frame)
        self.cam_2 = Camera(number=cam_no_2, frame=frame)

    def start_threads(self, cam_1, cam_2):
        print("Start threads")
        if not self.eyes_active: return
        # Start cam threads
        model_1, model_2 = YOLO("models/Arm/Arm.pt"), YOLO("models/Arm/Arm.pt")
        thread1 = threading.Thread(target=self.camera_thread, args=(cam_1, model_1), daemon=True)
        thread2 = threading.Thread(target=self.camera_thread, args=(cam_2, model_2), daemon=True)
        thread1.start()
        thread2.start()

        # Start identified objects thread
        threading.Thread(target=self.identified_objects_thread, daemon=True).start()

        # Set up but don't start threads that use the camera
        self.calibration_thread = threading.Thread(target=self.calibrate, daemon=True)
        self.capture_image_thread = threading.Thread(target=self.capture_image, daemon=True)

    def camera_thread(self, cam, model):
        if not self.eyes_active: return
        print(f"Starting camera {cam.number}")
        for results in model.track(source=cam.number, show=False, stream=True, persist=True, verbose=False):
            print("Camera thread", cam.number)
            frame = results.orig_img
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if cam.single_capture:
                filename = self.model.get_next_save_file(cam.number)
                cv2.imwrite(filename, results.orig_img)
                cam.single_capture = False

            cam.last_frame = frame

            # Add boxes and tracker id to frame
            cam.boxes = get_boxes(results.boxes)
            for class_id, x1, y1, x2, y2, tracker_id in cam.boxes:
                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
                cv2.putText(frame, str(tracker_id), (x1 + 10, y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)


            # Show Image
            frame_tk = ImageTk.PhotoImage(image=Image.fromarray(frame))
            cam.canvas.create_image(0, 0, image=frame_tk, anchor=NW)

            # Pause
            sleep(self.thread_delay)

    def identified_objects_thread(self):
        if not self.eyes_active: return
        print("Starting identified objects thread")
        while True:
            print("Identified objects thread")
            increment_items(self)
            dual_boxes = combine_boxes(self.cam_1.boxes, self.cam_2.boxes)
            self.update_items_using_boxes(dual_boxes)
            self.update_tree(tree=self.t_items, tree_items=self.items)
            sleep(self.thread_delay)

    def get_head_coords(self):
        print("Get head coords")
        if not self.eyes_active: return
        # Give time for camera threads to run
        sleep(self.thread_delay * 1.2)
        sleep(2)

        for item in self.items:
            if item.label == 0: return item.x1, item.y1, item.x2, item.y2
            print("Head coords:", item.x1, item.y1, item.x2, item.y2)

    def start_calibration_thread(self):
        print("Start calibration thread")
        if not self.eyes_active: return
        if not self.arm_active: return
        self.calibration_thread.start()

    def start_capture_image_thread(self):
        print("Start capture image thread")
        if not self.eyes_active: return
        self.capture_image_thread.start()

    def capture_image(self):
        print("Capture image")
        if not self.eyes_active: return
        for cam in [self.cam_1, self.cam_2]:
            cam.single_capture = True

    # ------------------
    # ---- ITEMS -------
    # ------------------

    def update_items_using_boxes(self, boxes):
        print("Update items using boxes")
        if not boxes: return
        for box in boxes:
            label, i1, x1, y1, i2, x2, y2 = box
            existing = False
            for item in self.items:
                if item.i1 == i1 and item.i2 == i2:
                    item.update(box)
                    existing = True
            if not existing:
                new = Item(self, box)

    def identified_object_selected(self, e):
        print("Identifed object selected")
        if datetime.now() < self.item_selected_time + timedelta(seconds=1):
            print("Debouncing effective")
            return

        self.item_selected_time = datetime.now()

        tree = self.t_items
        tree_item = tree.focus()
        values = tree.item(tree_item)['values']

        if len(values) < 8: return
        for count, var in enumerate(self.selected_object_variables):
            var.set(values[count])

        if self.move_to_selected_object and self.arm_active:
            self.move(self.v_x.get(), self.v_y.get(), max(self.v_z.get(), 30))

        if self.item_function.get() == "Move Arm To Item":
            if self.arm_active:
                self.add_text("Moving arm to item")
            else:
                self.add_text("Can't move - the arm isn't active")
        if self.item_function.get() == "Send to Excel":
            label_text, i1, x1, y1, i2, x2, y2, x, y, z = values
            data = [x1, y1, x2, y2, x, y, z]
            point = Point(data=data)
            add_points_to_excel([point], start_column=self.excel_column)
            self.excel_column += 1
            text = "Sending item coordinates to Excel: " + str(data)
            self.add_text(text)

    # ----------------
    # ---- ARM -------
    # ----------------

    def calibrate(self):
        print("Calibrate")
        if not self.arm_active: return
        self.clear_calibration_points()
        x1, x2 = self.v_x_min.get(), self.v_x_max.get()
        y1, y2 = self.v_y_min.get(), self.v_y_max.get()
        z1, z2 = self.v_z_min.get(), self.v_z_max.get()
        self.arm.calibrate(self, x1, x2, y1, y2, z1, z2)
        self.update_tree(self.t_calibration_points, self.scene.calibration_points)
        add_model_to_excel(self.scene)

    def move(self, x, y, z):
        print("Move")
        if not self.arm_active: return
        self.arm.move(x, y, z)

    # ------------------------
    # ---- CALIBRATION -------
    # -----------------------

    def calibration_entry_box_changed(self, e):
        print("Calibration entry box changed")
        self.update_calibration_buttons()

    def run_calibration_button(self, number):
        print("Run calibration button")
        if not self.arm_active: return
        if number in [0, 2, 4, 6]: x = self.v_x_min.get()
        else:                      x = self.v_x_max.get()
        if number in [0, 1, 4, 5]: y = self.v_y_min.get()
        else:                      y = self.v_y_max.get()
        if number in [0, 1, 2, 3]: z = self.v_z_min.get()
        else:                      z = self.v_z_max.get()
        self.move(x, y, z)

    def clear_calibration_points(self):
        print("Clear calibration points")
        # print("Clearing calibration points")
        db_clear_calibration_points(self.scene.name)    # Remove from database
        self.scene.calibration_points = []              # Remove from scene
        self.clear_tree(self.t_calibration_points)      # Remove from tree

    def calibration_point_selected(self, e):
        print("Calibration point selected")
        tree = self.t_calibration_points
        item = tree.focus()

    def model_to_xlsx(self):
        print("Model to xlsx")
        var_strings = ["x1", "y1", "x2", "y2", "x1 / (x2 + d)", "x1 / (y2 + d)", "y1 / (x2 + d)", "y1 / (y2 + d)", "x2 / (x1 + d)", "x2 / (y1 + d)", "y2 / (x1 + d)", "y2 / (y1 + d)"]

        text = ""
        for coef, var_string in zip(self.scene.model_x.coef_, var_strings):
            text += str(round(coef,1)) + var_string + " + "
        # self.add_text("Model X:", text[:-3])

        for name, coefs in [("Model X:", self.scene.model_x.coef_), ("Model Y:", self.scene.model_y.coef_), ("Model Z:", self.scene.model_z.coef_)]:
            text = ""
            for coef, var_string in zip(coefs, var_strings):
                text += str(round(coef, 1)) + var_string + " + "
            # self.add_text(name, text[:-3])

        add_model_to_excel(self.scene)
        add_points_to_excel(self.scene.calibration_points)








App(
    arm_active=False,
    eyes_active=True,
)