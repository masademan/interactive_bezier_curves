import numpy as np
import tkinter as tk
from typing import Callable
from tkinter import messagebox
from bezier_curve import get_bezier_curve_points


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
    frame: tk.Frame,
    section_name: str,
    from_: int,
    to: int,
    increment: int = 1,
    font_size: int = 11,
    command: Callable | str = "",
    use_float: bool = False,
) -> tuple[tk.IntVar, tk.Spinbox, tk.Button]:
    tk.Label(frame, text=section_name, font=("Arial", font_size), bg=frame.cget("bg")).pack(padx=5, pady=5)

    if not use_float:
        val_var = tk.IntVar(value=from_)
    else:
        val_var = tk.DoubleVar(value=from_)
    spinbox = tk.Spinbox(frame, from_=from_, to=to, increment=increment, textvariable=val_var, command=command)
    spinbox.pack(fill=tk.X, padx=5, pady=5)

    if command != "":
        spinbox.bind("<Return>", command)

    confirm = tk.Button(frame, text="Submit", command=command)
    confirm.pack(fill=tk.X, padx=5, pady=5)

    return val_var, spinbox, confirm


def distance_bewteen_two_points(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def in_circle_area(mouse_x: float, mouse_y: float, circle_x: float, circle_y: float, circle_radius: float) -> tuple[bool, float]:
    dist = distance_bewteen_two_points(mouse_x, mouse_y, circle_x, circle_y)
    return dist <= circle_radius, dist


def coord_in_list(coord_to_find: np.ndarray, all_coords: list[np.ndarray]) -> bool:
    for coord in all_coords:
        if (coord_to_find == coord).all():
            return True
    
    return False


class BezierGUI:
    def __init__(self, title="Bezier GUI", debug=False):
        self.debug = debug

        # Initialize window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.minsize(1080, 825)

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

        self.canvas.bind("<Configure>", self.draw)
        
        self.canvas.bind("<Button-1>", lambda event: print("Clicked"))
        self.canvas.bind("<Button-3>", lambda event: print("Right Clicked"))
        self.canvas.bind("<B1-Motion>", lambda event: print("Click + Drag"))
        self.canvas.bind("<ButtonRelease-1>", lambda event: print("Released"))

        # Right frame (controls)
        self.right_frame = tk.Frame(self.main_frame, width=200, padx=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Controls
        tk.Label(self.right_frame, text="Controls", font=("Arial", 12, "bold")).pack(pady=10)

        # Grid control
        self.grid_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.grid_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.grid_settings_frame,
            text="Grid settings",
            font=("Arial", 12, "bold"),
            bg="gray75",
        ).pack(padx=5, pady=5)
        self.grid_cell_size = 50
        self.grid_cell_size_var, self.grid_cell_size_spinbox, self.grid_cell_size_confirm = create_number_input(
            self.grid_settings_frame, "Grid cell size", 25, 500, increment=25, font_size=11, command=self.set_grid_cell_size
        )
        self.grid_cell_size_var.set(self.grid_cell_size)

        # Number of control points
        self.control_point_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.control_point_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.control_point_settings_frame,
            text="Control point settings",
            font=("Arial", 12, "bold"),
            bg="gray75",
        ).pack(padx=5, pady=5)
        self.num_control_points = 4
        self.num_control_points_var, self.num_control_points_spinbox, self.num_control_points_confirm = create_number_input(
            self.control_point_settings_frame, "Num control points", 2, 5, font_size=11, command=self.set_num_control_points
        )
        self.num_control_points_var.set(self.num_control_points)

        self.control_points = [
            np.array([-2, 0]),
            np.array([-1.75, 2]),
            np.array([1.75, 2]),
            np.array([2, 0]),
        ]

        # Size of control points
        self.control_point_radius = 7
        self.control_point_radius_var, self.control_point_radius_spinbox, self.control_point_radius_confirm = create_number_input(
            self.control_point_settings_frame, "Control point radius", 1, 30, font_size=11, command=self.set_control_point_radius, use_float=True
        )
        self.control_point_radius_var.set(self.control_point_radius)

        # Show lines between control points
        self.show_control_lines_var = tk.BooleanVar()
        self.show_control_lines_checkbox = tk.Checkbutton(
            self.control_point_settings_frame,
            text="Show lines between\ncontrol points",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_control_lines_var,
            command=self.draw_control_points,
        )
        self.show_control_lines_checkbox.pack(fill=tk.X, pady=5)

        # Bezier curve settings
        self.bezier_curve_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.bezier_curve_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.bezier_curve_settings_frame,
            text="Bezier curve settings",
            font=("Arial", 12, "bold"),
            bg="gray75",
        ).pack(padx=5, pady=5)

        self.left_bezier_settings_frame = tk.Frame(self.bezier_curve_settings_frame, bg="gray75")
        self.left_bezier_settings_frame.pack(fill=tk.Y, pady=5, side=tk.LEFT)

        self.right_bezier_settings_frame = tk.Frame(self.bezier_curve_settings_frame, bg="gray75")
        self.right_bezier_settings_frame.pack(fill=tk.Y, pady=5, side=tk.RIGHT)

        self.sample_point_radius = 5
        self.sample_point_radius_var, self.sample_point_radius_spinbox, self.sample_point_radius_confirm = create_number_input(
            self.left_bezier_settings_frame, "Sample point radius", 1, 20, font_size=11, command=self.set_sample_point_radius
        )
        self.sample_point_radius_var.set(self.sample_point_radius)

        self.curve_linewidth = 2
        self.curve_linewidth_var, self.curve_linewidth_spinbox, self.curve_linewidth_confirm = create_number_input(
            self.left_bezier_settings_frame, "Curve linewidth", 1, 10, font_size=11, command=self.set_curve_linewidth
        )
        self.curve_linewidth_var.set(self.curve_linewidth)

        self.curve_resolution = 5
        self.resolution_var, self.resolution_spinbox, self.resolution_confirm = create_number_input(
            self.right_bezier_settings_frame, "Curve resolution", 1, 300, font_size=11, command=self.set_curve_resolution
        )
        self.resolution_var.set(self.curve_resolution)

        # Show sampled points in Bezier curve
        self.show_points_var = tk.BooleanVar()
        self.show_points_checkbox = tk.Checkbutton(
            self.right_bezier_settings_frame,
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

    def set_grid_cell_size(self, _event=None):
        if not self.num_submission(self.grid_cell_size_spinbox, "grid cell size"):
            return

        self.grid_cell_size = int(self.limit_to_spinbox_range(self.grid_cell_size_spinbox, self.grid_cell_size_var.get()))
        self.grid_cell_size_var.set(self.grid_cell_size)

        self.draw()

    def set_num_control_points(self, _event=None):
        if not self.num_submission(self.num_control_points_spinbox, "number of control points"):
            return

        if self.num_control_points_var.get() - self.num_control_points > 1:
            messagebox.showerror("number of control points error", "When increasing the number of control points, it must be done one by one")
            self.num_control_points_var.set(self.num_control_points)
            return

        self.num_control_points = int(self.limit_to_spinbox_range(self.num_control_points_spinbox, self.num_control_points_var.get()))
        self.num_control_points_var.set(self.num_control_points)

        # Remove points
        while len(self.control_points) > self.num_control_points:
            self.control_points.pop()

        # Add points
        if len(self.control_points) < self.num_control_points:
            middle_w = self.canvas.winfo_width() // 2 + 1
            middle_h = self.canvas.winfo_height() // 2 + 1

            offset = self.grid_cell_size // 2

            canvas_x = (middle_w - offset) % self.grid_cell_size + offset
            canvas_y = (middle_h - offset) % self.grid_cell_size + offset
            
            new_coord = np.array(self.canvas_to_coord((canvas_x, canvas_y)))
            
            if coord_in_list(new_coord, self.control_points):
                messagebox.showerror("number of control points error", "First move the new control point out of the way")
                self.num_control_points -= 1
                self.num_control_points_var.set(self.num_control_points)
                return

            self.control_points.append(new_coord)

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_control_point_radius(self, _event=None):
        if not self.num_submission(self.control_point_radius_spinbox, "size of control points", True):
            return

        self.control_point_radius = self.limit_to_spinbox_range(self.control_point_radius_spinbox, self.control_point_radius_var.get())
        self.control_point_radius = (
            int(self.control_point_radius) if abs(int(self.control_point_radius) - self.control_point_radius) <= 1e-5 else self.control_point_radius
        )
        self.control_point_radius_var.set(self.control_point_radius)

        self.draw_control_points()

    def set_curve_resolution(self, _event=None):
        if not self.num_submission(self.resolution_spinbox, "resolution"):
            return

        self.curve_resolution = int(self.limit_to_spinbox_range(self.resolution_spinbox, self.resolution_var.get()))
        self.resolution_var.set(self.curve_resolution)

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_sample_point_radius(self, _event=None):
        if not self.num_submission(self.sample_point_radius_spinbox, "number of control points"):
            return

        self.sample_point_radius = int(self.limit_to_spinbox_range(self.sample_point_radius_spinbox, self.sample_point_radius_var.get()))
        self.sample_point_radius_var.set(self.sample_point_radius)

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_curve_linewidth(self, _event=None):
        if not self.num_submission(self.curve_linewidth_spinbox, "curve linewidth", True):
            return

        self.curve_linewidth = self.limit_to_spinbox_range(self.curve_linewidth_spinbox, self.curve_linewidth_var.get())
        self.curve_linewidth = int(self.curve_linewidth) if abs(int(self.curve_linewidth) - self.curve_linewidth) <= 1e-5 else self.curve_linewidth
        self.curve_linewidth_var.set(self.curve_linewidth)

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

    def canvas_to_coord(self, canvas_coord: tuple[float, float] | np.ndarray) -> tuple[float, float]:
        x, y = canvas_coord

        middle_w = self.canvas.winfo_width() // 2 + 1
        middle_h = self.canvas.winfo_height() // 2 + 1

        new_x = (x - middle_w) / self.grid_cell_size
        new_y = (middle_h - y) / self.grid_cell_size

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

        if self.show_control_lines_var.get():
            for i in range(len(self.control_points) - 1):
                p1 = self.control_points[i]
                p2 = self.control_points[i + 1]

                self.canvas.create_line(
                    *self.coord_to_canvas(p1), *self.coord_to_canvas(p2), fill="gray55", width=2, tags="control_points", dash=(5, 2)
                )

        for control_point in self.control_points:
            draw_circle(self.canvas, *self.coord_to_canvas(control_point), self.control_point_radius, fill="red", tags="control_points")

    def draw_bezier_curve(self):
        self.canvas.delete("bezier_curve")

        bezier_curve_points = get_bezier_curve_points(self.control_points, int(self.curve_resolution))

        for i in range(len(bezier_curve_points) - 1):
            p1 = bezier_curve_points[i]
            p2 = bezier_curve_points[i + 1]

            self.canvas.create_line(
                *self.coord_to_canvas(p1),
                *self.coord_to_canvas(p2),
                fill="blue",
                width=self.curve_linewidth,
                tags="bezier_curve",
            )

            if i != 0:
                draw_circle(
                    self.canvas,
                    *self.coord_to_canvas(p1),
                    self.curve_linewidth // 2,
                    fill="blue",
                    outline="blue",
                    tags="bezier_curve",
                )

        if self.show_points_var.get():
            for i in range(1, len(bezier_curve_points) - 1):
                point = bezier_curve_points[i]
                draw_circle(self.canvas, *self.coord_to_canvas(point), self.sample_point_radius, fill="dodger blue", tags="bezier_curve")

    def reset(self):
        # Reset grid cell size
        self.grid_cell_size = 50
        self.grid_cell_size_var.set(self.grid_cell_size)

        # Reset control points
        self.control_points = [
            np.array([-2, 0]),
            np.array([-1.75, 2]),
            np.array([1.75, 2]),
            np.array([2, 0]),
        ]

        self.num_control_points = 4
        self.num_control_points_var.set(self.num_control_points)

        # Reset control point radius
        self.control_point_radius = 7
        self.control_point_radius_var.set(self.control_point_radius)

        # Reset sample point radius
        self.sample_point_radius = 5
        self.sample_point_radius_var.set(self.sample_point_radius)

        # Reset curve linewidth
        self.curve_linewidth = 2
        self.curve_linewidth_var.set(self.curve_linewidth)

        # Reset resolution
        self.curve_resolution = 5
        self.resolution_var.set(self.curve_resolution)

        # Reset show sampled points
        self.show_points_var.set(False)

        self.draw()

        if self.debug:
            print(self.root.winfo_width(), self.root.winfo_height())

    def run_gui(self):
        self.root.mainloop()

    def quit(self, _event=None):
        self.root.destroy()


if __name__ == "__main__":
    bezier_gui = BezierGUI(debug=True)
    bezier_gui.run_gui()
