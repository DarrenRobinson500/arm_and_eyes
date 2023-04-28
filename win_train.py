from model import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# plt.style.use('fivethirtyeight')
# plt.xkcd()

data_names = ["epoch", "box_loss", "class_loss", "dfl_loss", "precision", "recall", "map50", "map95", "val_box_loss",
              "val_class_loss", "val_dfl_loss", "pg0", "pg1", "pg2"]

class App_Train:
    def __init__(self):
        self.name = "View Training Progress"
        self.window = ttk.Window(themename='litera')
        self.window.title(self.name)
        self.window.geometry("2020x800+0+0")
        load_models()
        self.model = models[0]
        self.data_name = "map50"

        self.set_up_frames()
        self.set_up_left_frame()
        self.set_up_right_frame()

        self.update_trees()

        self.set_up_keys()

        # self.print_runs()

        self.window.mainloop()

    def print_runs(self):
        for run in self.model.runs:
            print(run)

    def set_up_frames(self):
        side_width = 130
        center_width = 1300

        # Vertical Frames
        self.frame_a = Frame(self.window, width=side_width, height=800)
        self.frame_b = Frame(self.window, height=800)
        self.frame_a.pack(side="left")
        self.frame_b.pack(side="left")

    def set_up_left_frame(self):
        self.t_model = new_tree(heading="Model", frame=self.frame_a, height=10, width=150, command_if_changed=self.tree_changed, side="left")
        self.t_options = new_tree(heading="Variable", frame=self.frame_a, height=10, width=150, command_if_changed=self.tree_changed, side="left")

        self.t_runs = new_tree_complex(self.frame_a, heading="Model Log", height=10,
                                       columns=("No", "Size", "Run", "Time", "Epochs", "map50", "map95"),
                                       widths=(40, 100, 100, 100, 100, 100, 100), command_if_changed=self.tree_changed, side="left")

    def set_up_right_frame(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack()

    def update_trees(self):
        self.update_tree(self.t_model, models)
        self.update_tree_options()
        self.update_tree_runs()

    def update_tree_runs(self):
        tree = self.t_runs
        clear_tree(tree)
        for count, run in enumerate(self.model.runs):
            values = (run.number, run.size, run.run, time_format(run.time), run.epochs, map_format(run.map50), map_format(run.map95))
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=values)

    def update_tree_options(self):
        tree = self.t_options
        clear_tree(tree)
        for count, data_name in enumerate(data_names):
            tree.insert(parent='', index='end', iid=str(count), text="Parent", values=data_name)

    def update_tree(self, tree, list):
        x = tree.selection()
        number = get_number(x)
        clear_tree(tree)
        for item in list:
            tree.insert(parent='', index='end', iid=str(item.number), text="Parent", values=item.name)
        tree.selection_set(number)

    def tree_changed(self, e):
        tree = e.widget
        x = tree.selection()
        number = get_number(x)
        if tree == self.t_model:
            self.model = get_model(number)
            self.update_tree_runs()
            self.plot_graphs()

        if tree == self.t_options:
            self.data_name = data_names[number]
            self.plot_graphs()

        if tree == self.t_runs:
            run = self.model.get_run(number)
            csv_file = run.folder + "/results.csv"
            self.plot_graph(run)

    def plot_graph(self, run):
        self.ax.clear()
        self.plot_graphs()
        csv_file = run.folder + "/results.csv"
        data = np.genfromtxt(csv_file, delimiter=',', skip_header=1, names=data_names)
        self.ax.plot(data["epoch"], data[self.data_name], linewidth=1, color='b', label=f"Run {run.run}")
        self.canvas.draw()
        # plt.show()

    def plot_graphs(self):
        self.ax.clear()
        for run in self.model.runs:
            csv_file = run.folder + "/results.csv"
            data = np.genfromtxt(csv_file, delimiter=',', skip_header=1, names=data_names)
            self.ax.plot(data["epoch"], data[self.data_name], linewidth=0.5, color='k', label=f"Run {run.run}")
        self.ax.set_xlabel('Epoch')
        self.ax.set_ylabel('Accuracy')
        self.ax.set_title(self.data_name)
        self.ax.legend()
        self.canvas.draw()
        # plt.show()

    def set_up_keys(self):
        self.window.bind('<Escape>', lambda e: self.exit(e))

    def exit(self, e):
        self.window.destroy()

# print(plt.style.available)

App_Train()

