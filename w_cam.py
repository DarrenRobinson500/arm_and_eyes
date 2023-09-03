from model import *
from scene import *
from camera import *
from arduino_2 import *
from pos import *
from excel import *
label_ids_1 = []

class App:
    def __init__(self, dual=True, yolo=True, arm_connected=True):
        self.name = "Viewer"
        self.window = ttk.Window(themename='litera')
        self.window.title(self.name)
        self.window.geometry("2020x1000+0+0")
        self.dual = dual
        self.update_delay = 1
        self.arm_connected = arm_connected

        self.yolo = yolo
        if not self.yolo:
            ttk.Label(self.window, text="YOLO Disabled", style='danger.Inverse.TLabel', justify="center").pack(side=TOP, fill=BOTH)

        load_models()

        self.object, self.v_x1, self.v_y1, self.v_x2, self.v_y2, self.v_x, self.v_y, self.v_z = StringVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()
        self.selected_object_variables = [self.object, self.v_x1, self.v_y1, self.v_x2, self.v_y2, self.v_x, self.v_y, self.v_z]
        self.v_x_min, self.v_x_max, self.v_y_min, self.v_y_max, self.v_z_min, self.v_z_max = IntVar(), IntVar(), IntVar(), IntVar(), IntVar(), IntVar()
        self.calibration_variables = [self.v_x_min, self.v_x_max, self.v_y_min, self.v_y_max, self.v_z_min, self.v_z_max]

        self.set_up_frames()
        self.set_up_model()
        self.set_up_scene()
        self.set_up_left_frame()
        self.set_up_buttons()
        self.set_up_model_buttons(self.frame_2c)
        self.set_up_log(self.frame_2d)
        self.set_up_video_frame() # including setting up videos
        self.set_up_right_frame(self.frame_c)

        self.update_trees()
        self.set_up_keys()


        self.model_active = (len(self.scene.calibration_points) >= 4)

        if self.arm_connected:
            self.connect_to_arm()
            if len(self.scene.calibration_points) < 4:
                self.calibrate()
            self.move_arm_to_pos(450, -100, 55)

        self.update_camera()
        self.window.mainloop()

    def set_up_frames(self):
        # Set up frames
        side_width = 130
        center_width = 1300

        # Vertical Frames
        self.frame_a = Frame(self.window, width=side_width, height=800)
        self.frame_b = Frame(self.window, height=800)
        self.frame_c = Frame(self.window, width=side_width, height=800)
        self.frame_a.pack(side="left", anchor=NW)
        self.frame_b.pack(side="left", anchor=NW)
        self.frame_c.pack(side="left", anchor=NW)

        # Hortizontal Frames for center
        self.frame_0 = Frame(self.frame_b, width=center_width, height=80)
        self.frame_1 = Frame(self.frame_b, width=center_width, height=400, bg="white")
        self.frame_2 = Frame(self.frame_b, width=center_width, height=80)
        self.frame_3 = Frame(self.frame_b, width=center_width, height=320, highlightbackground="white", highlightthickness=1)
        self.frame_0.pack(anchor=NW)
        self.frame_1.pack(anchor=NW)
        self.frame_2.pack()
        self.frame_3.pack(anchor=NW)

        self.frame_2a = Frame(self.frame_2, width=center_width//4, height=80)
        self.frame_2b = Frame(self.frame_2, width=center_width//4, height=80)
        self.frame_2c = Frame(self.frame_2, width=center_width//4, height=80)
        self.frame_2d = Frame(self.frame_2, width=center_width//4, height=80)
        self.frame_2a.pack(side="left", anchor=NW, padx=20)
        self.frame_2b.pack(side="left", anchor=NW, padx=20)
        self.frame_2c.pack(side="left", anchor=NW, padx=20)
        self.frame_2d.pack(side="left", anchor=NW, padx=20)

    def set_up_model(self):
        self.model = models[0]

    def set_up_scene(self):
        if len(scenes) == 0:
            self.scene = Scene("Scene A")
            print("Made new scene")
        else:
            self.scene = scenes[0]

    def set_up_left_frame(self):
        self.t_model = new_tree(heading="Model", frame=self.frame_a, height=4, width=150, command_if_changed=self.tree_changed)

        self.t_scene = new_tree(heading="Scene", frame=self.frame_a, height=4, width=150, command_if_changed=self.tree_changed)
        Button(self.frame_a, text="New Scene", command=self.new_scene).pack(fill="x", expand=True, pady=5)
        self.v_scene_name = StringVar(self.frame_a, value="Scene A")
        Entry(self.frame_a, textvariable=self.v_scene_name).pack()

        self.t_cam_0 = new_tree(heading="Camera 1", frame=self.frame_a, height=3, width=150, command_if_changed=self.tree_changed)
        self.t_cam_1 = new_tree(heading="Camera 2", frame=self.frame_a, height=3, width=150, command_if_changed=self.tree_changed)
        self.cam_0 = cameras[0]
        self.cam_1 = cameras[1]


    def new_scene(self):
        name = self.v_scene_name.get()
        # print(name)
        Scene(name)
        self.update_tree(self.t_scene, scenes)

    def update_trees(self):
        #                tree          values
        self.update_tree(self.t_model, models)
        self.update_tree(self.t_scene, scenes)
        self.update_tree(self.t_cam_0, cameras)
        self.update_tree(self.t_cam_1, cameras)
        self.update_tree_calibration_points() # Calibration tree uses slightly different update process

    def update_tree(self, tree, items):
        if tree == self.t_model: number = self.model.number
        if tree == self.t_scene: number = self.scene.number
        if tree == self.t_cam_0: number = self.cam_0.number
        if tree == self.t_cam_1: number = self.cam_1.number
        self.clear_tree(tree)
        for item in items:
            # print("Updating Tree:" item.number, item.name)
            try:
                tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=item.name)
            except:
                pass
        tree.selection_set(number)

    def update_tree_calibration_points(self):
        tree = self.t_calibration_points
        current_item_number = tree.focus()
        self.clear_tree(tree)
        # print("Calibration points when setting up calibration point tree:", len(scene_A.calibration_points))

        for count, item in enumerate(self.scene.calibration_points):
            # print(item.data_and_error)
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=item.data_and_error)
        tree.selection_set(current_item_number)

    def update_tree_identified_objects(self, boxes):
        tree = self.t_identified_objects
        current_item_number = tree.focus()
        self.clear_tree(tree)
        for count, box in enumerate(boxes):
            class_id, x1, y1, x2, y2 = box
            label_name = self.model.get_label(class_id).name
            # print("Update tree - identified objects:", label_name)
            box[0] = label_name
            # print("Model Active:", self.model_active)
            if self.model_active:
                box.extend(self.scene.pos(x1, y1, x2, y2))
                # print("Extended box:", box)
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=box)
        try:
            tree.selection_set(current_item_number)
        except:
            pass

    def tree_changed(self, e):
        tree = e.widget
        x = tree.selection()
        number = get_number(x)
        if tree == self.t_model: self.model = get_model(number)
        if tree == self.t_scene: self.scene = get_scene(number)
        if tree == self.t_cam_0: self.cam_0 = get_cam(number)
        if tree == self.t_cam_1: self.cam_1 = get_cam(number)

    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def set_up_video_frame(self):
        self.cam_0 = Camera(number=0)
        self.canvas0 = Canvas(self.frame_1, width=self.cam_0.width, height=self.cam_0.height)
        self.cam_0.set_canvas(self.canvas0)
        self.canvas0.pack(side=LEFT)
        if self.dual:
            self.cam_1 = Camera(number=1)
            self.canvas1 = Canvas(self.frame_1, width=self.cam_1.width, height=self.cam_1.height)
            self.cam_1.set_canvas(self.canvas1)
            self.canvas1.pack(side=LEFT)

    def set_up_buttons(self):
        ttk.Label(self.frame_2a, text="Commands", style="primary", font=('Helvetica', 12)).pack(pady=10, )

        # Image capture
        Button(self.frame_2a, text="Capture Image", command=self.capture_image).pack(anchor=NW, pady=10)

        # Recording
        self.v_recording = StringVar(self.frame_b)
        Checkbutton(self.frame_2a, text="Record", variable=self.v_recording, onvalue="Recording", offvalue="Not recording").pack(anchor=NW)
        self.v_recording.set('0')

        # Commands
        ttk.Label(self.frame_2b, text="Angles", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
        self.v_command_line_angles = StringVar(self.frame_2b, value="p 1500 300 300")
        Entry(self.frame_2b, textvariable=self.v_command_line_angles).pack(anchor=NW)
        Button(self.frame_2b, text="Run Command (angles)", command=self.run_command_angles).pack(anchor=NW, fill="x", expand=True, pady=5)

        ttk.Label(self.frame_2b, text="Position", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
        self.v_command_line_pos = StringVar(self.frame_2b, value="400 -100 55")
        Entry(self.frame_2b, textvariable=self.v_command_line_pos).pack()
        Button(self.frame_2b, text="Run Command (position)", command=self.run_command_position).pack(anchor=NW, fill="x", expand=True, pady=5)

    def set_up_model_buttons(self, frame):
        # Label
        ttk.Label(frame, text="Model", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
        Button(frame, text="Model to xlsx", command=self.model_to_xlsx).pack(anchor=NW, pady=10)

    def model_to_xlsx(self):
        var_strings = ["x1", "y1", "x2", "y2", "x1 / (x2 + d)", "x1 / (y2 + d)", "y1 / (x2 + d)", "y1 / (y2 + d)", "x2 / (x1 + d)", "x2 / (y1 + d)", "y2 / (x1 + d)", "y2 / (y1 + d)"]

        text = ""
        for coef, var_string in zip(self.scene.model_x.coef_, var_strings):
            text += str(round(coef,1)) + var_string + " + "
        self.add_text("Model X:", text[:-3])

        for name, coefs in [("Model X:", self.scene.model_x.coef_), ("Model Y:", self.scene.model_y.coef_), ("Model Z:", self.scene.model_z.coef_)]:
            text = ""
            for coef, var_string in zip(coefs, var_strings):
                text += str(round(coef, 1)) + var_string + " + "
            self.add_text(name, text[:-3])

        add_model_to_excel(self.scene)
        add_points_to_excel(self.scene.calibration_points)

    def set_up_log(self, frame):
        # Label
        ttk.Label(frame, text="Log", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
        # Internal frame for text box
        own_frame = Frame(frame)
        own_frame.pack(pady=5, anchor=NW)
        # Scroll bar
        text_scroll = Scrollbar(own_frame)
        text_scroll.pack(side=RIGHT, fill=Y)
        # Text box
        self.text = Text(own_frame, width=80, height=10, wrap=WORD, yscrollcommand=text_scroll.set)
        self.text.pack()
        text_scroll.config(command=self.text.yview)

    def set_up_right_frame(self, frame):
        # self.add_manual_calibration_entry(self.frame_c)

        self.t_calibration_points = new_tree_complex(
            frame=frame, heading="Calibration Points", height=10, columns=("x1", "y1", "x2", "y2", "x", "y", "z", "Err"), widths=(50, 50, 50, 50, 50, 50, 50, 50),
            command_if_changed=self.calibration_point_selected)
        self.update_tree_calibration_points()
        # self.calibration_point = None
        Button(frame, text="Re-calibrate", command=self.calibrate).pack(anchor=NW, pady=10, expand=True)
        # Button(self.frame_c, text="Clear", command=self.clear_calibration_points).pack(pady=10, anchor=NW)
        self.add_calibration_min_max(frame)

        self.t_identified_objects = new_tree_complex(
            frame=frame, heading="Identified objects", height=7, columns=("Object", "x1", "y1", "x2", "y2", "x", "y", "z"), widths=(60, 30, 30, 30, 30, 30, 30, 30),
            command_if_changed=self.identified_object_selected)

        self.add_selected_object(frame)

    def add_selected_object(self, frame):
        own_frame = Frame(frame)
        own_frame.pack(anchor=NW, padx=10)
        for count, x in enumerate(("Object", "x1", "y1", "x2", "y2", "x", "y", "z")):
            Label(own_frame, text=x).grid(row=0, column=count)
            Label(own_frame, textvariable=self.selected_object_variables[count], width=6).grid(row=1, column=count)

    def add_manual_calibration_entry(self, frame):
        Button(frame, text="New Calibration Point", command=self.new_calibration_point).pack(fill=X, expand=True)

        own_frame = Frame(frame, width=40, height=80)
        own_frame.pack(pady=5)
        for count, x in enumerate(("x1", "y1", "x2", "y2", "x", "y", "z")):
            Label(own_frame, text=x).grid(row=0, column=count)
            if count <= 3:
                Label(own_frame, textvariable=self.coord_variables[count], width=5).grid(row=1, column=count)
            else:
                Entry(own_frame, textvariable=self.coord_variables[count], width=5).grid(row=1, column=count)

    def add_calibration_min_max(self, frame):
        # Heading
        ttk.Label(frame, text="Calibration Area", style="primary", font=('Helvetica', 12)).pack(anchor=NW, pady=10)
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

        # for row in [1, 2]:
        #     for column in [1, 2, 3, 4]:
        #         new = Button(own_frame, text="XXX", command=lambda : self.run_calibration_button(count), width=10)
        #         new.grid(row=row, column=column)
        #         self.calibration_buttons.append(new)
        #         count += 1

        self.update_calibration_buttons()

    def calibration_entry_box_changed(self, e):
        self.update_calibration_buttons()

    def update_calibration_buttons(self):
        self.calibration_buttons[0].config(text=f"{self.v_x_min.get()} {self.v_y_min.get()} {self.v_z_min.get()}")
        self.calibration_buttons[1].config(text=f"{self.v_x_max.get()} {self.v_y_min.get()} {self.v_z_min.get()}")
        self.calibration_buttons[2].config(text=f"{self.v_x_min.get()} {self.v_y_max.get()} {self.v_z_min.get()}")
        self.calibration_buttons[3].config(text=f"{self.v_x_max.get()} {self.v_y_max.get()} {self.v_z_min.get()}")
        self.calibration_buttons[4].config(text=f"{self.v_x_min.get()} {self.v_y_min.get()} {self.v_z_max.get()}")
        self.calibration_buttons[5].config(text=f"{self.v_x_max.get()} {self.v_y_min.get()} {self.v_z_max.get()}")
        self.calibration_buttons[6].config(text=f"{self.v_x_min.get()} {self.v_y_max.get()} {self.v_z_max.get()}")
        self.calibration_buttons[7].config(text=f"{self.v_x_max.get()} {self.v_y_max.get()} {self.v_z_max.get()}")

    def run_calibration_button(self, number):
        if number in [0, 2, 4, 6]: x = self.v_x_min.get()
        else:                      x = self.v_x_max.get()
        if number in [0, 1, 4, 5]: y = self.v_y_min.get()
        else:                      y = self.v_y_max.get()
        if number in [0, 1, 2, 3]: z = self.v_z_min.get()
        else:                      z = self.v_z_max.get()
        print("Running command", x, y, z)
        self.move_arm_to_pos(x, y, z)

    def clear_calibration_points(self):
        # print("Clearing calibration points")
        db_clear_calibration_points(self.scene.name)    # Remove from database
        self.scene.calibration_points = []              # Remove from scene
        self.clear_tree(self.t_calibration_points)      # Remove from tree

    def calibration_point_selected(self, e):
        tree = self.t_calibration_points
        item = tree.focus()
        values = tree.item(item)['values']
        # self.add_text("Calibration point: ", values)

    def add_text(self, label, text):
        self.text.insert(END, label + str(text) + "\n")

    def identified_object_selected(self, e):
        tree = self.t_identified_objects
        item = tree.focus()
        values = tree.item(item)['values']

        if len(values) < 8: return
        for count, var in enumerate(self.selected_object_variables):
            var.set(values[count])

        # self.add_text("Identified object:", values)
        # if len(values) < 5: return
        # for number, var in enumerate(self.coord_variables[0:4], 1):
        #     var.set(values[number])
        # print("Selected:", values)
        # object, x1, y1, x2, y2, x, y, z = values
        # z = max(z + 30, 30)
        # print("Moving to:", x, y, z)
        #
        # if distance(x, y) > 400:
        #     self.move_arm_to_pos(x, y, z)
        # else:
        #     print("Too close to home - not moving")
        # print(dir(e))
        # result = inspect.getmembers(e, lambda a: not (inspect.isroutine(a)))
        # for x in result:
        #     print(x)

    def move_to_identified_object(self):
        tree = self.t_identified_objects
        item = tree.focus()
        print("Move to (item):", item)
        values = tree.item(item)['values']
        if len(values) < 5: return
        x, y, z = values[5], values[6], values[7]
        print("Move to (x, y, z):", x, y, z)
        result = get_angles(x, y, z)
        command(result_to_text(result))

    def key_stroke(self, e):
        if e.keysym == "Delete":
            tree = self.t_calibration_points
            x = tree.selection()
            number = get_number(x)
            print(number)
            print(self.scene.calibration_points[number])
            self.scene.calibration_points.pop(number)
            self.update_tree_calibration_points()

    def set_up_keys(self):
        self.window.bind('<Escape>', lambda e: self.exit(e))
        self.t_calibration_points.bind('<KeyPress>', self.key_stroke)

    def exit(self, e):
        if self.arm_connected:
            command("p 0 0 0")
        self.window.destroy()

    def capture_image(self):
        is_open0, frame_cv0, frame0 = self.cam_0.get_frame(model=self.model, record=False)
        if is_open0:
            filename = self.model.get_next_save_file("A")
            cv2.imwrite(filename, frame_cv0)
        if self.dual:
            is_open1, frame_cv1, frame1 = self.cam_1.get_frame(model=self.model, record=False)
            if is_open1:
                filename = self.model.get_next_save_file("B")
                cv2.imwrite(filename, frame_cv1)

    def run_command_angles(self):
        requested_command = self.v_command_line_angles.get()
        # print("Run command:", requested_command)
        command(requested_command)

    def run_command_position(self):
        requested_command = self.v_command_line_pos.get()
        x, y, z = integers(requested_command.split())
        self.move_arm_to_pos(x, y, z)
        result = get_angles(x, y, z)
        # print(result_to_text(result))
        command(result_to_text(result))

    def move_arm_to_pos(self, x, y, z):
        result = get_angles(x, y, z)
        print(result)
        command(result_to_text(result))

    def connect_to_arm(self):
        if not self.arm_connected:
            print("Parameters set to not connect to arm. Not connecting.")
            return
        get_port()
        print("Waiting for homing")
        wait_for_homing()

    def calibrate(self):
        if not self.arm_connected:
            print("Parameters set to not connect to arm. Not connecting.")
            return
        self.clear_calibration_points()

        for z in [30,80]:
            for x in [400, 500]:
                for y in [-50, -150]:
                    result = get_angles(x, y, z)
                    # print(result_to_text(result))
                    command(result_to_text(result))
                    self.capture_image()
                    result = self.get_head_coords()
                    if result:
                        x1, y1, x2, y2 = result
                        data = x1, y1, x2, y2, x, y, z
                        self.new_calibration_point(data)
                    else:
                        print("Didn't create calibration point")
                        self.capture_image()
        self.update_tree_calibration_points()
        add_model_to_excel(self.scene)
        self.add_text("Excel:", "Calibration data updated")

    def new_calibration_point(self, data):
        # values = self.v_x1.get(), self.v_y1.get(), self.v_x2.get(), self.v_y2.get(), self.v_x.get(), self.v_y.get(), self.v_z.get()
        print("New calibration point:", data)
        self.model_active = self.scene.new_calibration_point(data)
        self.update_tree_calibration_points()

    def get_single_coords(self, result, canvas, video):
        box_array = []
        if result:
            is_open, frame_cv, frame = result
            if is_open:
                photo_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
                canvas.create_image(0, 0, image=photo_image, anchor=NW)
                if self.yolo:
                    boxes = self.model.boxes_live(frame_cv)
                    for id in self.cam_0.labels: self.canvas0.delete(id)
                    for class_id, x1, y1, x2, y2 in boxes:
                        box_array.append((class_id, (x1 + x2) // 2, (y1 + y2) // 2, 0, 0))
                        label = self.model.get_label(class_id)
                        if label is None: label = self.model.get_label(0)
                        label_id = self.canvas0.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
                        video.labels.append(label_id)
        return box_array


    def get_head_coords(self):
        result = self.cam_0.get_frame(self.model, record=False)
        boxes_0 = self.get_single_coords(result=result, canvas=self.canvas0, video=self.cam_0)
        # print("Boxes 0:", boxes_0)
        result = self.cam_1.get_frame(self.model, record=False)
        boxes_1 = self.get_single_coords(result=result, canvas=self.canvas1, video=self.cam_1)
        # print("Boxes 1:", boxes_1)
        if len(boxes_0) > 0 and len(boxes_1) > 0:
            result = boxes_0[0][1], boxes_0[0][2], boxes_1[0][1], boxes_1[0][2]
            # print("Boxes:", result)
        else:
            # print("Lengths:", len(boxes_0), len(boxes_1))
            result = None
        return result

    def update_camera(self):
        recording = self.v_recording.get() == "Recording"
        result = self.cam_0.get_frame(self.model, record=recording)
        boxes, boxes0, boxes1 = [], None, None
        if result:
            is_open0, frame_cv0, frame0 = result

            if is_open0:
                self.frame0 = ImageTk.PhotoImage(image=Image.fromarray(frame0))
                self.canvas0.create_image(0, 0, image=self.frame0, anchor=NW)
                if self.yolo:
                    boxes0 = self.model.boxes_live(frame_cv0)
                    for id in self.cam_0.labels: self.canvas0.delete(id)
                    for class_id, x1, y1, x2, y2 in boxes0:
                        boxes.append((class_id, (x1 + x2) // 2, (y1 + y2) // 2, 0, 0))
                        label = self.model.get_label(class_id)
                        if label is None: label = self.model.get_label(0)
                        label_id = self.canvas0.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
                        self.cam_0.labels.append(label_id)
        if self.dual:
            # print("Self dual")
            result = self.cam_1.get_frame(self.model, record=recording)
            if result:
                is_open1, frame_cv1, frame1 = result
                if is_open1:
                    self.frame1 = ImageTk.PhotoImage(image=Image.fromarray(frame1))
                    self.canvas1.create_image(0, 0, image=self.frame1, anchor=NW)
                    if self.yolo:
                        boxes1 = self.model.boxes_live(frame_cv1)
                        # print(boxes)
                        for id in self.cam_1.labels: self.canvas1.delete(id)
                        for class_id, x1, y1, x2, y2 in boxes1:
                            boxes.append((class_id, 0, 0, (x1 + x2) // 2, (y1 + y2) // 2))
                            label = self.model.get_label(class_id)
                            if label is None: label = self.model.get_label(0)
                            label_id = self.canvas1.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
                            self.cam_1.labels.append(label_id)

        if boxes0 and boxes1:
            boxes = self.combine_boxes(boxes0, boxes1)
            self.update_tree_identified_objects(boxes)
        else:
            clear_tree(self.t_identified_objects)

        self.window.after(self.update_delay, self.update_camera)

    def combine_boxes(self, boxes0, boxes1):
        boxes0 = get_box_centers(boxes0)
        boxes1 = get_box_centers(boxes1)
        boxes0 = sorted(boxes0, key=lambda x: x[1])
        boxes1 = sorted(boxes1, key=lambda x: x[1])

        boxes = []
        for box0, box1 in zip(boxes0, boxes1):
            class0, x0, y0 = box0
            class1, x1, y1 = box1
            boxes.append([class0, x0, y0, x1, y1])

        return boxes

    def update_class_based(self):
        recording = self.v_recording.get() == "Recording"
        for video in self.videos:
            # print(video.name)
            is_open, frame_cv0, frame = video.get_frame(self.model, record=recording)
            if is_open:
                self.frame0 = ImageTk.PhotoImage(image=Image.fromarray(frame))
        #         canvas.create_image(0, 0, image=frame, anchor=NW)
        #         self.canvas0.create_image(0, 0, image=frame, anchor=NW)

            # is_open0, frame_cv0, frame0 = self.video0.get_frame(self.model, record=recording)
            # if is_open0:
            #     self.frame0 = ImageTk.PhotoImage(image=Image.fromarray(frame0))
            #     self.canvas0.create_image(0, 0, image=self.frame0, anchor=NW)
            #     print(video.canvas)
                video.canvas.create_image(0, 0, image=self.frame0, anchor=NW)
        self.window.after(1, self.update)





# App(dual=True, yolo=True, arm_connected=True)
App(dual=True, yolo=True, arm_connected=False)
# App(dual=True, yolo=False, arm_connected=False)
# App(dual=False, yolo=False, arm_connected=False)