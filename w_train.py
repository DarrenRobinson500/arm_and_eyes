from model import *
from utilities import *

IMAGE_FILTER_ALL = -2
IMAGE_FILTER_NO_LABEL = -1


class Win_Train:
    def __init__(self):
        self.window = ttk.Window(themename='darkly')
        self.window.title("Neural Network Trainer")
        self.window.geometry("2020x1000+0+0")
        self.max_perspective_adj = 2
        self.canvas_height = 480
        
        self.set_up_models()

        self.set_up_screen()
        self.initialise()
        self.update_label_info()
        self.update_model_info()
        self.trees = [self.t_label, self.t_model, self.t_image_filter, self.t_image]

        self.set_up_keys()

        self.update_tree_model_log()
        self.refresh()

        self.window.mainloop()

    def set_up_models(self):
        load_models()
        self.model = models[0]
        self.label = self.model.labels[0]
        self.image = None

    def set_up_screen(self):
        self.set_up_frames()
        self.set_up_left_frame()
        self.set_up_headings()
        self.set_up_canvas()
        self.set_up_middle_buttons()
        self.set_up_label_section()
        self.set_up_model_section()
        self.set_up_image_tree()

    def set_up_frames(self):
        side_width = 130
        center_width = 1300

        self.frame_a = Frame(self.window, width=side_width, height=1000)
        self.frame_b = Frame(self.window, width=center_width, height=1000)
        self.frame_c = Frame(self.window, width=side_width, height=1000)
        self.frame_a.pack(side="left")
        self.frame_b.pack(side="left")
        self.frame_c.pack(side="left")

        # Hortizontal Frames for center
        self.frame_0 = Frame(self.frame_b, width=center_width, height=80, bg="blue", highlightbackground="white",
                        highlightthickness=1)
        self.frame_1 = Frame(self.frame_b, width=center_width, height=400, bg="white")
        self.frame_2 = Frame(self.frame_b, width=center_width, height=80)
        self.frame_3 = Frame(self.frame_b, width=center_width, height=320, highlightbackground="white", highlightthickness=1)
        self.frame_0.pack()
        self.frame_1.pack()
        self.frame_2.pack()
        self.frame_3.pack()

        # Vertical Frames in 3
        self.frame_0a = Frame(self.frame_0, width=center_width // 3)
        self.frame_0b = Frame(self.frame_0, width=center_width // 3)
        self.frame_0c = Frame(self.frame_0, width=center_width // 3)
        self.frame_0a.pack(side="left", padx=50)
        self.frame_0b.pack(side="left", padx=50)
        self.frame_0c.pack(side="left", padx=50)

        self.frame_3a = Frame(self.frame_3)
        self.frame_3a1 = Frame(self.frame_3a)
        self.frame_3a2 = Frame(self.frame_3a)
        self.frame_3b = Frame(self.frame_3)
        self.frame_3b1 = Frame(self.frame_3b)
        self.frame_3b2 = Frame(self.frame_3b)
        self.frame_3c = Frame(self.frame_3)
        self.frame_3c1 = Frame(self.frame_3c)
        self.frame_3c2 = Frame(self.frame_3c)
        self.frame_3d = Frame(self.frame_3)
        self.frame_3d1 = Frame(self.frame_3d)
        self.frame_3d2 = Frame(self.frame_3d)
        self.frame_3a.pack(side="left", fill="both", expand=True)
        self.frame_3b.pack(side="left", fill="both", expand=True)
        self.frame_3c.pack(side="left", fill="both", expand=True)
        self.frame_3d.pack(side="left", fill="both", expand=True)
        self.frame_3a1.pack(fill="both", expand=True)
        self.frame_3a2.pack(side="bottom")
        self.frame_3b1.pack(fill="both", expand=True)
        self.frame_3b2.pack(side="bottom")
        self.frame_3c1.pack(fill="both", expand=True)
        self.frame_3c2.pack(side="bottom")
        self.frame_3d1.pack(fill="both", expand=True)
        self.frame_3d2.pack(side="bottom")

    def set_up_left_frame(self):
        self.t_label = new_tree(heading="Label", frame=self.frame_a, height=10, width=200, command_if_changed=self.tree_changed_label)
        self.t_model = new_tree(heading="Model", frame=self.frame_a, height=10, width=200, command_if_changed=self.tree_changed_model)

        # Frame A - Delete mode checkbox
        self.var_delete = StringVar(self.window)
        cb_delete_mode = Checkbutton(self.frame_a, text="Delete", variable=self.var_delete, onvalue="Delete Mode",
                                     offvalue="Label Mode")
        cb_delete_mode.pack()
        self.var_delete.set('0')

    def set_up_headings(self):
        self.v_label_name = StringVar()
        self.l_label_name = Label(self.frame_0a, textvariable=self.v_label_name, font="Calibri 24 bold")
        self.l_label_name.pack(side="left")
        self.v_image_name = StringVar()
        self.l_image_name = Label(self.frame_0b, textvariable=self.v_image_name, font="Calibri 24 bold")
        self.l_image_name.pack(side="left")
        self.v_image_count = StringVar()
        self.l_image_count = Label(self.frame_0c, textvariable=self.v_image_count, font="Calibri 24 bold")
        self.l_image_count.pack(side="left")

    def set_up_canvas(self):
        self.canvas = Canvas(self.frame_1, width=640, height=self.canvas_height, bg="white")
        self.canvas.pack(side="left")
        self.canvas.bind('<Button-1>', self.mouse_click)
        self.canvas.bind('<Leave>', self.mouse_rectangle_clear)
        self.canvas.bind('<Motion>', self.mouse_move)
        self.canvas_m = Canvas(self.frame_1, width=640, height=self.canvas_height, bg="white")
        self.canvas_m.pack(side="left")
        self.image_container = self.canvas.create_image(0, 0, anchor="nw")
        self.image_container_m = self.canvas_m.create_image(0, 0, anchor="nw")

    def set_up_middle_buttons(self):
        buttons = [("Previous", self.prev_image), ("Next", self.next_image), ("Next Unlabelled ", self.next_unlabelled_image), ("Copy", self.copy_modelled_labels)]
        button_row(buttons, self.frame_2)

    def set_up_label_section(self):
        ttk.Label(self.frame_3a1, text="Labels", style="primary", font=('Helvetica', 12)).grid(row=0, column=0, sticky=N)
        for text, column, row in [("Name", 0, 1), ("Colour", 0, 2), ("Width", 2, 1), ("Height", 2, 2)]:
            ttk.Label(self.frame_3a1, text=text, padding=10).grid(row=row, column=column)
        self.v_label_w = IntVar(self.window)
        self.v_label_h = IntVar(self.window)
        self.e_name = Entry(self.frame_3a1)
        self.e_colour = Entry(self.frame_3a1)
        self.s_label_w = Spinbox(self.frame_3a1, from_=5, to=100, increment=5, textvariable=self.v_label_w, command=self.spin_x_changed, width=6)
        self.s_label_h = Spinbox(self.frame_3a1, from_=5, to=100, increment=5, textvariable=self.v_label_h, command=self.spin_y_changed, width=6)
        self.e_name.grid(row=1, column=1)
        self.e_colour.grid(row=2, column=1)
        self.s_label_w.grid(row=1, column=3)
        self.s_label_h.grid(row=2, column=3)
        buttons = [("Add Label", self.add_label), ("Save Label", self.save_label), ("Remove Label", self.remove_label)]
        button_row(buttons, self.frame_3a2)

    def set_up_model_section(self):
        ttk.Label(self.frame_3b1, text="Models", style="primary", font=('Helvetica', 12)).grid(row=0, column=0)
        for count, text in enumerate(["Name:", "Size", "Epochs", "Threshold", "Training time:", "Map50:", "Map95:"], 1):
            Label(self.frame_3b1, text=text, pady=5, padx=10).grid(row=count, column=0, sticky=W)

        self.v_model_name = StringVar(self.window)
        self.e_model_name = Entry(self.frame_3b1, textvariable=self.v_model_name)
        self.e_model_name.grid(row=1, column=1)
        self.v_model_name.set(self.model.name)

        self.v_model_size = StringVar(self.window, value=self.model.size)
        ttk.Combobox(self.frame_3b1, values=["nano", "small", "medium", "large", "x large"], textvariable=self.v_model_size).grid(
            row=2, column=1)

        self.v_model_epochs = new_entry_box(frame=self.frame_3b1, initial_value=self.model.epochs, row=3, column=1)
        self.v_model_threshold = new_entry_box(frame=self.frame_3b1, initial_value=self.model.threshold, row=4, column=1)

        buttons = [("Add Model", self.add_model), ("Save Model", self.save_model)]
        button_row(buttons, self.frame_3b2)
        buttons = [("Train Model", self.train_model), ("Remove Model", self.remove_model)]
        button_row(buttons, self.frame_3c2)

        self.t_model_log = new_tree_complex(self.frame_3c1, heading="Model Log", height=5, columns=("Size", "Run", "Time", "Epochs", "map50", "map95"), widths=(70, 60, 60, 60, 60, 60))

    def set_up_image_tree(self):
        self.t_image_filter = new_tree(heading="Image Filter", frame=self.frame_c, height=5, width=200, command_if_changed=self.tree_changed_image_filter)

        f_image_tree = Frame(self.frame_c)
        f_image_tree.pack(pady=10, padx=10)
        s_image_tree = Scrollbar(f_image_tree)
        s_image_tree.pack(side=RIGHT, fill=Y)

        self.t_image = ttk.Treeview(f_image_tree, height=30, yscrollcommand=s_image_tree.set, selectmode="extended")
        s_image_tree.config(command=self.t_image.yview)
        self.t_image['columns'] = ("Name", "Labels")
        self.t_image.column("#0", width=0, minwidth=0)
        self.t_image.column("Name", anchor=W, width=90)
        self.t_image.column("Labels", anchor=W, width=90)
        self.t_image.heading("#0", text="")
        self.t_image.heading("Name", text="File", anchor=W)
        self.t_image.heading("Labels", text="Labels", anchor=W)
        # update_tree_images()
        self.t_image.pack()
        self.t_image.tag_configure("oddrow", background="white")
        self.t_image.tag_configure("evenrow", background="lightblue")
        self.t_image.bind('<<TreeviewSelect>>', self.image_tree_changed)
        self.t_image.tag_configure("red", background="red")
        self.t_image.tag_configure("blue", background="blue")
        self.t_image.tag_configure("green", background="green")

    def update_label_info(self):
        write(self.e_name, self.label.name)
        write(self.e_colour, self.label.colour)
        self.v_label_w.set(self.label.width)
        self.v_label_h.set(self.label.height)

    def initialise(self):
        self.set_current_label()
        self.set_current_image()
        self.image_filter = None
        self.mouse_id = None
        self.label_ids = []
        self.label_m_ids = []

    def set_current_label(self):
        x = self.t_label.selection()
        if len(x) == 0:
            label_number = 0
        else:
            label_number = int(x[0])
        self.label = self.model.get_label(label_number)
        self.v_label_w.set(self.label.width // 2)
        self.v_label_h.set(self.label.height // 2)

    def set_current_model(self):
        x = self.t_model.selection()
        if len(x) == 0:
            number = 0
        else:
            number = int(x[0])
        self.model = get_model(number)
        # print("Set current model:", self.model, number, x)
        self.update_model_info()

    def set_current_image_filter(self):
        x = self.t_image_filter.selection()
        if len(x) == 0:
            number = 0
        else:
            number = int(x[0])
        self.image_filter = number
        print("Set current image filter:", self.image_filter)

    def set_current_image(self):
        x = self.t_image.selection()
        if len(x) == 0:
            number = 0
        else:
            number = int(x[0])
        self.image = self.model.get_image(number)
        # print("Set current image:", self.image.image_file)

    def set_up_keys(self):
        self.window.bind('<KeyPress>', self.key_stroke)
        self.window.bind('<Escape>', lambda e: self.close_win(e))

    def key_stroke(self, e):
        if e.char == "q": self.v_label_h.set(self.v_label_h.get() + 1)
        if e.char == "a": self.v_label_h.set(self.v_label_h.get() - 1)
        if e.char == ".": self.v_label_w.set(self.v_label_w.get() + 1)
        if e.char == ",": self.v_label_w.set(self.v_label_w.get() - 1)
        if e.char in ["q", "a", ",", "."]:
            self.spin_y_changed()
            self.spin_x_changed()
            x, y = self.window.winfo_pointerxy()
            x0, y0 = self.canvas.winfo_rootx(), self.canvas.winfo_rooty()
            self.draw_mouse_rectangle(x - x0, y - y0)
        if e.keysym == "Down": self.next_image()
        if e.keysym == "Up": self.prev_image()

    def close_win(self, e):
        self.window.destroy()

    def update_tree(self, tree):
        clear_tree(tree)
        if tree == self.t_image:
            self.update_tree_images()
            return
        if tree == self.t_image_filter:
            self.update_tree_image_filter()
            return

        if tree == self.t_label:
            tree_list = self.model.labels
            current = self.label
        elif tree == self.t_model:
            tree_list = models
            current = self.model
        for item in tree_list:
            tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=item.name)
        tree.selection_set(current.number)

    def update_tree_image_filter(self):
        tree = self.t_image_filter
        clear_tree(tree)
        tree_list = self.model.labels
        # tree.insert(parent='', index='end', iid=str(len(tree_list)), text="Parent", values="All")
        # tree.insert(parent='', index='end', iid=str(len(tree_list)), text="Parent", values="All")
        tree.insert(parent='', index='end', iid=IMAGE_FILTER_ALL, text="Parent", values="All_Images")
        tree.insert(parent='', index='end', iid=IMAGE_FILTER_NO_LABEL, text="Parent", values="No_Labels")
        for item in tree_list:
            print("Update tree image filter:", item.number)
            tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=item.name)
        print("Update tree image filter:", len(tree_list))
        tree.selection_set(-2)

    def update_tree_images(self):
        tree = self.t_image
        clear_tree(tree)
        for count, item in enumerate(self.model.images):
            manual_labels = int(len(item.labels))
            model_labels = len(item.box_list)
            tag = "normal"
            if manual_labels < model_labels: tag = "red"
            if manual_labels > model_labels: tag = "blue"
            if manual_labels == 0: tag = "green"
            to_show = False
            if self.image_filter == IMAGE_FILTER_ALL:
                to_show = True
            elif self.image_filter == IMAGE_FILTER_NO_LABEL:
                if len(item.labels) == 0: to_show = True
            else:
                print("Label Filter")
                to_show = self.image_filter in item.get_label_list()

            # print("Update tree images:", item, "Filter selected:", self.image_filter, "Labels on image:", item.get_label_list(), "To show:", to_show)
            # if len(item.get_label_list()) > 0:
            #     print(type(self.image_filter), type(item.get_label_list()[0]))
            if to_show:
                tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=(item.name, f"{int(len(item.labels))} {len(item.box_list)}"), tags=tag)
        if self.image:
            try:
                tree.selection_set(self.image.number)
            except:
                pass

    def update_tree_model_log(self):
        tree = self.t_model_log
        clear_tree(tree)
        logs = db_read_model_run_log(self.model)
        for count, log in enumerate(logs):
            model, date, run, size, epochs, time, map50, map95, folder = log
            map50 = map_format(map50)
            map95 = map_format(map95)

            values = (size, run, time_format(time), epochs, map50, map95)
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=values)

    def refresh(self):
        self.model.write_labels_to_file()
        for tree in self.trees: self.update_tree(tree)
        self.draw_label_rectangles()
        self.draw_label_rectangles_m()
        self.v_label_name.set(self.label.name.replace("_", " ").title())
        # print("Available videos:", self.model.available_videos())
        # self.v_video_name.set(self.model.available_videos())
        if self.image:
            self.v_image_name.set(self.image.name)
            self.v_image_count.set(self.model.image_count())

    # Canvas
    def get_rectangle(self, x, y):
        perspective_adj = (y / self.canvas_height) * self.max_perspective_adj + (1 - y / self.canvas_height) * 1
        x1, y1 = int(x - self.label.width // 2 * perspective_adj), int(y - self.label.height // 2 * perspective_adj)
        x2, y2 = int(x + self.label.width // 2 * perspective_adj), int(y + self.label.height // 2 * perspective_adj)
        w, h = int(self.image.image.width() * 1), int(self.image.image.height() * 1)
        return x1, y1, x2, y2, w, h

    def mouse_click(self, e):
        # A mouse click to create new label
        if self.var_delete.get() == "Delete Mode":
            self.image.delete_label(e.x, e.y)
        else:
            x1, y1, x2, y2, w, h = self.get_rectangle(e.x, e.y)
            self.image.add_label(self.label.number, x1, y1, x2, y2, w, h)
        self.draw_label_rectangles()
        self.update_tree_images()

    def draw_mouse_rectangle(self, x, y):
        if self.mouse_id: self.canvas.delete(self.mouse_id)
        x1, y1, x2, y2, w, h = self.get_rectangle(x, y)

        self.mouse_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.label.colour, width=2)

    def mouse_rectangle_clear(self, e):
        if self.mouse_id: self.canvas.delete(self.mouse_id)

    def mouse_move(self, e):
        if self.var_delete.get() == "Delete Mode": return
        self.draw_mouse_rectangle(e.x, e.y)

    # Labels
    def spin_x_changed(self):
        self.label.width = int(self.s_label_w.get())
        self.label.model.write_labels_to_file()

    def spin_y_changed(self):
        self.label.height = int(self.s_label_h.get())
        self.label.model.write_labels_to_file()

    def add_label(self):
        MyLabel(name=self.e_name.get(), model=self.model, colour=self.e_colour.get(), width=int(self.v_label_w.get()),
                height=int(self.v_label_h.get()))
        self.refresh()

    def save_label(self):
        self.label.name = self.e_name.get()
        self.label.colour = self.e_colour.get()
        self.label.width = int(self.v_label_w.get())
        self.label.height = int(self.v_label_h.get())
        self.refresh()

    def remove_label(self):
        self.label.delete()
        self.refresh()

    # Models
    def add_model(self):
        Model(self.v_model_name.get())
        self.refresh()

    def save_model(self):
        self.model.save_name(self.v_model_name.get())
        self.model.save_size(self.v_model_size.get())
        self.model.save_threshold(self.v_model_threshold.get())
        self.model.save_epochs(self.v_model_epochs.get())
        self.show_image()

    def train_model(self):
        self.save_model()  # This makes sure any udpates on the screen are
        self.model.train()
        self.update_model_info()
        self.update_tree_model_log()

    def update_model_info(self):
        for count, text in enumerate([self.model.time_f(), map_format(self.model.map50), map_format(self.model.map95)], 4):
            Label(self.frame_3b1, text=str(text), pady=10, padx=10).grid(row=count + 1, column=1, sticky=W)
        # self.v_video_name.set(self.model.available_videos())

    def remove_model(self):
        delete_model(self.model)
        self.model = models[0]
        self.refresh()

    # Videos
    def load_videos(self):
        self.model.load_videos()
        self.refresh()

    # Images
    def next_image(self):
        self.image = self.model.get_next_image(self.image)
        self.t_image.selection_set(self.image.number)
        self.show_image()

    def next_unlabelled_image(self):

        self.image = self.model.get_next_unlabelled_image(self.image)
        self.t_image.selection_set(self.image.number)
        self.show_image()

    def prev_image(self):
        self.image = self.model.get_prev_image(self.image)
        self.t_image.selection_set(self.image.number)
        self.show_image()

    def show_image(self):
        if self.image:
            image = self.image.image
            self.canvas.itemconfig(self.image_container, image=image)
            self.canvas_m.itemconfig(self.image_container_m, image=image)
            self.draw_label_rectangles()
            self.draw_label_rectangles_m()

    def copy_modelled_labels(self):
        for id, x1, y1, x2, y2 in self.image.box_list:
            w, h = self.image.image.width(), self.image.image.height()
            self.image.add_label(id, x1, y1, x2, y2, w, h)
        self.next_image()

    def image_tree_changed(self, e):
        self.set_current_image()
        self.show_image()
        if self.image:
            self.v_image_name.set(self.image.name)
            self.v_image_count.set(self.model.image_count())
        else:
            self.v_image_name.set("No image")

    def draw_label_rectangles(self):
        # Remove existing labels
        # print("Add label rectangles:", self.label_ids)
        for id in self.label_ids: self.canvas.delete(id)
        self.label_ids = []

        if self.image is None: return

        # Add new labels
        width, height = self.image.image.width(), self.image.image.height()
        for class_id, x, y, w, h in self.image.labels:
            label = self.model.get_label(class_id)
            if label is None: label = self.model.get_label(0)
            x1, y1 = int(x * width), int(y * height)
            x2, y2 = int((x + w) * width), int((y + h) * height)
            label_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
            self.label_ids.append(label_id)

    def draw_label_rectangles_m(self):
        # Remove existing labels
        for id in self.label_m_ids: self.canvas_m.delete(id)
        self.label_m_ids = []

        # Add new labels
        boxes = self.model.boxes(self.image)

        for class_id, x1, y1, x2, y2 in boxes:
            label = self.model.get_label(class_id)
            if label is None: label = self.model.get_label(0)
            label_id = self.canvas_m.create_rectangle(x1, y1, x2, y2, outline=label.colour, width=2)
            self.label_m_ids.append(label_id)

    # Trees
    def tree_changed_label(self, e):
        self.set_current_label()
        self.e_name.delete(0, END)
        self.e_name.insert(0, self.label.name)
        self.e_colour.delete(0, END)
        self.e_colour.insert(0, self.label.colour)
        self.v_label_w.set(self.label.width)
        self.v_label_h.set(self.label.height)
        self.v_label_name.set(self.label.name)

    def tree_changed_model(self, e):
        self.set_current_model()
        self.e_model_name.delete(0, END)
        self.e_model_name.insert(0, self.model.name)
        self.update_tree(self.t_label)
        self.image = self.model.get_first_image()
        self.update_tree(self.t_image)

    def tree_changed_image_filter(self, e):
        self.set_current_image_filter()
        self.update_tree(self.t_image)


Win_Train()