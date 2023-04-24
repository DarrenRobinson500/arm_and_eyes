from model import *
from scene import *
from utilities import *
import inspect

label_ids_1 = []

class App:
    def __init__(self, dual=True, yolo=True):
        self.name = "Viewer"
        self.window = ttk.Window(themename='litera')
        self.window.title(self.name)
        self.window.geometry("2020x800+0+0")
        self.dual = dual
        self.yolo = yolo
        self.model_active = False

        Label(self.window, text=self.name, font=15, bg="blue", fg="white").pack(side=TOP, fill=BOTH)

        load_models()

        self.v_x1, self.v_y1, self.v_x2, self.v_y2, self.v_x, self.v_y, self.v_z = DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar(), DoubleVar()
        self.coord_variables = [self.v_x1, self.v_y1, self.v_x2, self.v_y2, self.v_x, self.v_y, self.v_z]

        self.set_up_frames()
        self.set_up_left_frame()
        self.set_up_buttons()
        self.set_up_video_frame()
        self.set_up_right_frame()

        self.update_trees()
        self.set_up_keys()

        # To be removed post testing
        self.new_calibration_point_initial_set_up()
        boxes = [[1, 0, 0, 0, 0], [1, 10, 0, 10, 0], [1, 0, 0, 0, 10], [1, 10, 0, 10, 10],]
        self.update_tree_identified_objects(boxes)

        self.window.mainloop()

    def set_up_frames(self):
        # Set up frames
        side_width = 130
        center_width = 1300

        # Vertical Frames
        self.frame_a = Frame(self.window, width=side_width, height=800)
        self.frame_b = Frame(self.window, height=800)
        self.frame_c = Frame(self.window, width=side_width, height=800)
        self.frame_a.pack(side="left")
        self.frame_b.pack(side="left")
        self.frame_c.pack(side="left")

        # Hortizontal Frames for center
        self.frame_0 = Frame(self.frame_b, width=center_width, height=80)
        self.frame_1 = Frame(self.frame_b, width=center_width, height=400, bg="white")
        self.frame_2 = Frame(self.frame_b, width=center_width, height=80)
        self.frame_3 = Frame(self.frame_b, width=center_width, height=320, highlightbackground="white", highlightthickness=1)
        self.frame_0.pack()
        self.frame_1.pack()
        self.frame_2.pack()
        self.frame_3.pack()

    def set_up_left_frame(self):
        self.t_model = new_tree(heading="Model", frame=self.frame_a, height=10, width=150, command_if_changed=self.tree_changed)
        self.model = models[0]
        self.t_scene = new_tree(heading="Scene", frame=self.frame_a, height=10, width=150, command_if_changed=self.tree_changed)
        if len(scenes) == 0:
            self.scene = Scene("Scene A")
        else:
            self.scene = scenes[0]

        Button(self.frame_a, text="New Scene", command=self.new_scene).pack(fill="x", expand=True, pady=5)
        self.v_scene_name = StringVar(self.frame_a, value="Scene A")
        Entry(self.frame_a, textvariable=self.v_scene_name).pack()

    def new_scene(self):
        name = self.v_scene_name.get()
        print(name)
        Scene(name)
        self.update_tree(self.t_scene, scenes)

    def update_trees(self):
        self.update_tree(self.t_model, models)
        self.update_tree(self.t_scene, scenes)
        self.update_tree(self.t_calibration_points, self.scene.calibration_points)

    def update_tree(self, tree, list):
        if tree == self.t_model: number = self.model.number
        if tree == self.t_scene: number = self.scene.number
        if tree == self.t_calibration_points: number = tree.focus()
        self.clear_tree(tree)
        for item in list:
            # print("Updating Tree:", item.name)
            tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=item.name)
        tree.selection_set(number)

    def update_tree_calibration_points(self):
        tree = self.t_calibration_points
        current_item_number = tree.focus()
        self.clear_tree(tree)
        for count, item in enumerate(self.scene.calibration_points):
            print(item)
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=item)
        tree.selection_set(current_item_number)

    def update_tree_identified_objects(self, boxes):
        tree = self.t_identified_objects
        current_item_number = tree.focus()
        self.clear_tree(tree)
        for count, box in enumerate(boxes):
            class_id, x1, y1, x2, y2 = box
            if self.model_active:
                box.extend(self.model.pos(x1, y1, x2, y2))
                print("Extended box:", box)
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=box)
        tree.selection_set(current_item_number)

    def tree_changed(self, e):
        tree = e.widget
        x = tree.selection()
        number = get_number(x)
        if tree == self.t_model: self.model = get_model(number)
        if tree == self.t_scene: self.scene = get_scene(number)

    # def tree_changed_scene(self, e):
    #     print("Tree changed: Scene")
    #     print(dir(e))
    #     x = self.t_scene.selection()
    #     number = get_number(x)
    #     self.scene = get_scene(number)

    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def set_up_video_frame(self):
        self.video0 = VideoCapture(video_source=0)
        self.canvas0 = Canvas(self.frame_1, width=self.video0.width, height=self.video0.height)
        self.video0.set_canvas(self.canvas0)
        self.canvas0.pack()
        self.videos = [self.video0, ]
        if self.dual:
            self.video1 = VideoCapture(video_source=1)
            self.canvas1 = Canvas(self.frame_1, width=self.video1.width, height=self.video1.height)
            self.video1.set_canvas(self.canvas1)
            self.canvas1.pack(side=LEFT)
            self.videos.append(self.video1, )
        self.update()

    def set_up_buttons(self):
        # Image capture
        Button(self.frame_2, text="Capture", command=self.capture_image).pack()

        # Recording
        self.v_recording = StringVar(self.frame_b)
        Checkbutton(self.frame_2, text="Record", variable=self.v_recording, onvalue="Recording", offvalue="Not recording").pack()
        self.v_recording.set('0')

    def set_up_right_frame(self):
        Button(self.frame_c, text="New Calibration Point", command=self.new_calibration_point).pack(fill=X, expand=True)

        self.frame_c_0 = Frame(self.frame_c, width=40, height=80)
        self.frame_c_0.pack(pady=5)
        for count, x in enumerate(("x1", "y1", "x2", "y2", "x", "y", "z")):
            Label(self.frame_c_0, text=x).grid(row=0, column=count)
            if count <= 3:
                Label(self.frame_c_0, textvariable=self.coord_variables[count], width=5).grid(row=1, column=count)
            else:
                Entry(self.frame_c_0, textvariable=self.coord_variables[count], width=5).grid(row=1, column=count)

        v_model_active = StringVar(value="Model Inactive")
        v_model_active.set("Hello")
        # print(v_model_active.get())
        # ttk.Label(self.frame_c, text="text", textvariable=v_model_active, font=('Helvetica', 12)).pack(pady=5, padx=5, fill="x", expand=True)
        # ttk.Label(self.frame_c, text="new", textvariable=v_model_active, style="TLabel", font=('Helvetica', 12)).pack(pady=5, padx=5, fill="x", expand=True)

        self.t_calibration_points = new_tree_complex(
            frame=self.frame_c, heading="Calibration Points", height=10, columns=("x1", "y1", "x2", "y2", "x", "y", "z"), widths=(40, 40, 40, 40, 40, 40, 40),
            command_if_changed=self.calibration_point_selected)
        self.calibration_point = None

        self.t_identified_objects = new_tree_complex(
            frame=self.frame_c, heading="Identified objects", height=10, columns=("Object", "x1", "y1", "x2", "y2", "x", "y", "z"), widths=(60, 30, 30, 30, 30, 30, 30, 30),
            command_if_changed=self.identified_object_selected)

        boxes = [[1, 0, 0, 0, 0], [1, 10, 0, 10, 0], [1, 0, 0, 0, 10], [1, 10, 0, 10, 10],]
        self.update_tree_identified_objects(boxes)

        # Button(self.frame_c, text="Run Calibration Model", command=self.run_calibration_model).pack(fill=X, expand=True)

    def calibration_point_selected(self, e):
        # print("Calibration point selected")
        pass

    def identified_object_selected(self, e):
        tree = self.t_identified_objects
        item = tree.focus()
        # print("Row", tree.item(item))
        # print("Row Values", tree.item(item)['values'])
        values = tree.item(item)['values']
        if len(values) < 5: return
        for number, var in enumerate(self.coord_variables[0:4], 1):
            var.set(values[number])

        # print(dir(e))
        # result = inspect.getmembers(e, lambda a: not (inspect.isroutine(a)))
        # for x in result:
        #     print(x)

    def new_calibration_point(self):
        values = self.v_x1.get(), self.v_y1.get(), self.v_x2.get(), self.v_y2.get(), self.v_x.get(), self.v_y.get(), self.v_z.get()
        print("New calibration point:", values)
        self.scene.new_calibration_point(self.v_x1.get(), self.v_y1.get(), self.v_x2.get(), self.v_y2.get(), self.v_x.get(), self.v_y.get(), self.v_z.get())
        self.update_tree_calibration_points()

    def new_calibration_point(self):
        values = self.v_x1.get(), self.v_y1.get(), self.v_x2.get(), self.v_y2.get(), self.v_x.get(), self.v_y.get(), self.v_z.get()
        print("New calibration point:", values)
        self.scene.new_calibration_point(self.v_x1.get(), self.v_y1.get(), self.v_x2.get(), self.v_y2.get(), self.v_x.get(), self.v_y.get(), self.v_z.get())
        self.update_tree_calibration_points()

    def new_calibration_point_initial_set_up(self):
        value_set = [
            ( 0, 0,  0,  0, 0, 0, 0),
            (10, 0, 10, 10, 10, 0, 0),
            ( 0, 0,  0, 10, 0, 10, 0),
            (10, 0, 10, 10, 10, 10, 0),
        ]
        for values in value_set:
            x1, y1, x2, y2, x, y, z = values
            print("New calibration point:", values)
            self.model_active = self.scene.new_calibration_point(x1, y1, x2, y2, x, y, z)
            print("Model active:", self.model_active)
        self.update_tree_calibration_points()

    def set_up_keys(self):
        self.window.bind('<Escape>', lambda e: self.exit(e))

    def exit(self, e):
        self.window.destroy()

    def capture_image(self):
        is_open0, frame_cv0, frame0 = self.video0.get_frame(model=self.model, record=False)
        if is_open0:
            filename = self.model.get_next_save_file()
            cv2.imwrite(filename, frame_cv0)
        if self.dual:
            is_open1, frame_cv1, frame1 = self.video1.get_frame(model=self.model, record=False)
            if is_open1:
                filename = self.model.get_next_save_file()
                cv2.imwrite(filename, frame_cv1)

    def update(self):
        recording = self.v_recording.get() == "Recording"
        is_open0, frame_cv0, frame0 = self.video0.get_frame(self.model, record=recording)
        if is_open0:
            self.frame0 = ImageTk.PhotoImage(image=Image.fromarray(frame0))
            self.canvas0.create_image(0, 0, image=self.frame0, anchor=NW)
            if self.yolo:
                boxes = self.model.boxes_live(frame_cv0)
                for id in self.video0.labels: self.canvas0.delete(id)
                for class_id, x1, y1, x2, y2 in boxes:
                    label = self.model.get_label(class_id)
                    if label is None: label = self.model.get_label(0)
                    label_id = self.canvas0.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
                    self.video0.labels.append(label_id)
        if self.dual:
            is_open1, frame_cv1, frame1 = self.video1.get_frame(self.model, record=recording)
            if is_open1:
                self.frame1 = ImageTk.PhotoImage(image=Image.fromarray(frame1))
                self.canvas1.create_image(0, 0, image=self.frame1, anchor=NW)
                if self.yolo:
                    boxes = self.model.boxes_live(frame_cv1)
                    # print(boxes)
                    for id in self.video1.labels: self.canvas1.delete(id)
                    for class_id, x1, y1, x2, y2 in boxes:
                        label = self.model.get_label(class_id)
                        if label is None: label = self.model.get_label(0)
                        label_id = self.canvas1.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
                        self.video1.labels.append(label_id)

        self.window.after(1, self.update)

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
                print(video.canvas)
                video.canvas.create_image(0, 0, image=self.frame0, anchor=NW)
        self.window.after(1, self.update)



class VideoCapture:
    def __init__(self, video_source):
        self.vid = cv2.VideoCapture(video_source)
        self.name = f"Camera {video_source}"
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.labels = []
        self.canvas = None

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

    # def get_frame(self):
    #     is_open, frame = self.vid.read()
    #     return is_open, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def __del__(self):
        self.vid.release()

App(dual=False, yolo=False)