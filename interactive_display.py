import numpy as np
import tkinter as tk
from typing import Callable
from tkinter import messagebox


# Helper functions
def draw_circle(canvas: tk.Canvas, x: float, y: float, radius: float, **kwargs) -> int:
    x0 = x - radius
    y0 = y - radius

    x1 = x + radius
    y1 = y + radius

    return canvas.create_oval(x0, y0, x1, y1, **kwargs)


def isnumeric(num_str: str, is_float: bool = False) -> bool:
    for char in num_str:
        if not (char in "0123456789" or (char == "." and is_float)):
            return False
    
    return True


def run_funcs(*funcs: Callable) -> None:
    for func in funcs:
        func()


def create_number_input(
    frame: tk.Frame, section_name: str, from_: int, to: int, font_size: int = 11, command: Callable | str = "", use_float: bool = False
) -> tuple[tk.IntVar, tk.Spinbox, tk.Button]:
    tk.Label(frame, text=section_name, font=("Arial", font_size), bg=frame.cget("bg")).pack(padx=5, pady=5)

    if not use_float: val_var = tk.IntVar(value=from_)
    else: val_var = tk.DoubleVar(value=from_)
    spinbox = tk.Spinbox(frame, from_=from_, to=to, increment=1, textvariable=val_var, command=command)
    spinbox.pack(fill=tk.X, padx=5, pady=5)

    confirm = tk.Button(frame, text="Submit", command=command)
    confirm.pack(fill=tk.X, padx=5, pady=5)

    return val_var, spinbox, confirm


class BezierGUI:
    def __init__(self, title="Test GUI"):
        # Initialize window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("600x400")
        self.root.minsize(570, 565)

        self.root.bind("<Control-w>", self.quit)
        self.root.bind("<Escape>", self.quit)

        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame (canvas)
        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas
        self.canvas = tk.Canvas(self.left_frame, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.grid_cell_size = 50  # Unit: pixels

        self.canvas.bind("<Configure>", self.draw)

        # Right frame (controls)
        self.right_frame = tk.Frame(self.main_frame, width=200, padx=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Controls
        tk.Label(self.right_frame, text="Controls", font=("Arial", 12, "bold")).pack(pady=10)

        # Number of control points
        self.control_point_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.control_point_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.control_point_settings_frame,
            text="Control point settings",
            font=("Arial", 12, "bold"),
            bg=self.control_point_settings_frame.cget("bg"),
        ).pack(padx=5, pady=5)
        self.num_control_points = 4
        self.num_control_points_var, self.num_control_points_spinbox, self.num_control_points_confirm = create_number_input(
            self.control_point_settings_frame, "Num control points", 2, 10, font_size=11, command=self.set_num_control_points
        )
        self.num_control_points_var.set(self.num_control_points)

        self.control_points = [
            np.array([-2, 0]),
            np.array([-1, 1]),
            np.array([1, 1]),
            np.array([2, 0]),
        ]

        # Size of control points
        self.point_size = 10
        self.point_size_var, self.point_size_spinbox, self.point_size_confirm = create_number_input(
            self.control_point_settings_frame, "Control point size", 1, 30, font_size=11, command=self.set_control_point_size, use_float=True
        )
        self.point_size_var.set(self.point_size)

        # Resolution of Bezier curve
        self.bezier_curve_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.bezier_curve_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.bezier_curve_settings_frame,
            text="Bezier curve settings",
            font=("Arial", 12, "bold"),
            bg=self.bezier_curve_settings_frame.cget("bg"),
        ).pack(padx=5, pady=5)
        self.curve_resolution = 5
        self.resolution_var, self.resolution_spinbox, self.resolution_confirm = create_number_input(
            self.bezier_curve_settings_frame, "Curve resolution", 1, 100, font_size=11, command=self.set_curve_resolution
        )
        self.resolution_var.set(self.curve_resolution)

        # Show simpled points in Bezier curve
        self.show_points_var = tk.BooleanVar()
        self.show_points_checkbox = tk.Checkbutton(
            self.bezier_curve_settings_frame,
            text="Show sampled points",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_points_var,
            command=lambda: run_funcs(self.draw_bezier_curve, self.draw_control_points),
        )
        self.show_points_checkbox.pack(fill=tk.X, pady=5)

        # Reset button
        btn_reset = tk.Button(self.right_frame, text="Reset", command=self.reset)
        btn_reset.pack(fill=tk.X, pady=5)

        # Quit button
        btn_quit = tk.Button(self.right_frame, text="Quit", command=self.quit)
        btn_quit.pack(fill=tk.X, pady=5)

    def set_num_control_points(self):
        if not self.num_submission(self.num_control_points_spinbox, "number of control points"):
            return

        self.num_control_points = self.limit_to_spinbox_range(self.num_control_points_spinbox, self.num_control_points_var.get())

        # Add or remove control points

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_control_point_size(self):
        if not self.num_submission(self.point_size_spinbox, "size of control points", True):
            return

        self.point_size = self.limit_to_spinbox_range(self.point_size_spinbox, self.point_size_var.get())

        self.draw_control_points()

    def set_curve_resolution(self):
        if not self.num_submission(self.resolution_spinbox, "resolution"):
            return

        self.curve_resolution = self.limit_to_spinbox_range(self.resolution_spinbox, self.resolution_var.get())

        self.draw_bezier_curve()
        self.draw_control_points()

    def limit_to_spinbox_range(self, spinbox: tk.Spinbox, value: int | float) -> int | float:
        return min(max(spinbox.cget("from"), value), spinbox.cget("to"))

    def num_submission(self, spinbox: tk.Spinbox, var_name: str, allow_float: bool = False) -> bool:
        if "." in spinbox.get() and not allow_float:
            messagebox.showerror(f"{var_name} error", f"The {var_name} MUST be an int, not '{spinbox.get()}'")
            return False

        if "-" in spinbox.get():
            messagebox.showerror(f"{var_name} error", f"The {var_name} MUST be positive, not '{spinbox.get()}'")
            return False

        if not isnumeric(spinbox.get(), allow_float):
            messagebox.showerror(
                f"{var_name} error", f"The {var_name} MUST be an {"int" if not allow_float else "float"} without letters, not '{spinbox.get()}'"
            )
            return False

        return True

    def coord_to_canvas(self, coord: tuple[float, float] | np.ndarray) -> tuple[float, float]:
        x, y = coord

        middle_w = self.canvas.winfo_width() // 2 + 1
        middle_h = self.canvas.winfo_height() // 2 + 1

        new_x = middle_w + x * self.grid_cell_size
        new_y = middle_h - y * self.grid_cell_size

        return new_x, new_y

    def draw(self, _event=None):
        self.draw_grid()
        self.draw_bezier_curve()
        self.draw_control_points()

    def draw_grid(self, _event=None):
        self.canvas.delete("grid_line")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        middle_w = width // 2 + 1
        middle_h = height // 2 + 1

        # Draw grid
        for i in range(middle_w, width, self.grid_cell_size):
            self.canvas.create_line(i, 0, i, height, tag="grid_line", fill="lightgray")
        for i in range(middle_w, -1, -self.grid_cell_size):
            self.canvas.create_line(i, 0, i, height, tag="grid_line", fill="lightgray")

        for i in range(middle_h, height, self.grid_cell_size):
            self.canvas.create_line(0, i, width, i, tag="grid_line", fill="lightgray")
        for i in range(middle_h, -1, -self.grid_cell_size):
            self.canvas.create_line(0, i, width, i, tag="grid_line", fill="lightgray")

        # Draw axis lines
        self.canvas.create_line(middle_w, 0, middle_w, height, tag="grid_line", fill="black", width=2)
        self.canvas.create_line(0, middle_h, width, middle_h, tag="grid_line", fill="black", width=2)

    def draw_control_points(self):
        self.canvas.delete("control_points")

        for control_point in self.control_points:
            draw_circle(self.canvas, *self.coord_to_canvas(control_point), self.point_size, fill="red", tags="control_points")

    def draw_bezier_curve(self):
        pass

    def reset(self):
        # Reset control points
        self.control_points = [
            np.array([-2, 0]),
            np.array([-1, 1]),
            np.array([1, 1]),
            np.array([2, 0]),
        ]

        self.num_control_points = 4
        self.num_control_points_var.set(self.num_control_points)

        # Reset resolution
        self.curve_resolution = 5
        self.resolution_var.set(self.curve_resolution)

        # print(self.root.winfo_width(), self.root.winfo_height())

    def run_gui(self):
        self.root.mainloop()

    def quit(self, _event=None):
        self.root.destroy()


if __name__ == "__main__":
    bezier_gui = BezierGUI()
    bezier_gui.run_gui()
