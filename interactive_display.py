import random
import numpy as np
import tkinter as tk
from tkinter.font import Font
from tkinter import messagebox
from fractions import Fraction
from typing import Callable, Literal
from bezier_curve import get_bezier_curve_points
from interactive_control_point_pos import show_control_point_pos_in_window

"""
TODO:
Add help guide
Button to show the coords of all the control points in a new window
"""

COORD_DECIMAL_ROUNDING = 2


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


def in_circle_area(
    mouse_x: float, mouse_y: float, circle_x: float, circle_y: float, circle_radius: float
) -> tuple[bool, float]:
    dist = distance_bewteen_two_points(mouse_x, mouse_y, circle_x, circle_y)
    return dist <= circle_radius, dist


def coord_in_list(coord_to_find: np.ndarray, all_coords: list[np.ndarray]) -> bool:
    for coord in all_coords:
        if (coord_to_find == coord).all():
            return True

    return False


def create_popup_window_toplevel(root: tk.Tk, title: str, quit_func: Callable) -> tk.Toplevel:
    popup_window = tk.Toplevel(root)
    popup_window.title(title)
    popup_window.protocol("WM_DELETE_WINDOW", quit_func)

    popup_window.bind("<Control-w>", quit_func)
    popup_window.bind("<Escape>", quit_func)

    return popup_window


class MoveablePointInfo:
    def __init__(self):
        self.mode: Literal["drag", "select", None] = None
        self.point_idx: int | None = None
        self.og_point_coord: tuple[float, float] | np.ndarray | None = None
        self.og_mouse_coord: tuple[float, float] | np.ndarray | None = None

    def set_mode(self, mode: Literal["drag", "select", None]) -> None:
        self.mode = mode

    def set_point_idx(self, idx: int) -> None:
        self.point_idx = idx

    def set_og_point_coord(self, coord: tuple[float, float] | np.ndarray) -> None:
        self.og_point_coord = coord

    def set_og_mouse_coord(self, coord: tuple[float, float] | np.ndarray) -> None:
        self.og_mouse_coord = coord

    def get_og_point_coord(self) -> np.ndarray:
        return np.array(self.og_point_coord)

    def get_mouse_movement(self, mouse_coord: tuple[float, float] | np.ndarray) -> np.ndarray:
        return np.array(mouse_coord) - np.array(self.og_mouse_coord)

    def get_og_point_coord_and_mouse_movement(
        self, mouse_coord: tuple[float, float] | np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        return self.get_og_point_coord(), self.get_mouse_movement(mouse_coord)

    def reset(self):
        self.mode = None
        self.point_idx = None
        self.og_point_coord = None
        self.og_mouse_coord = None


class BezierGUI:
    def __init__(self, title="Bezier GUI", debug=False):
        self.debug = debug

        self.colors = {
            "selected_control_point": "orange",
            "sampled_points": "dodger blue",
            "control_points": "red",
            "curve": "blue",
        }

        # Initialize window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.minsize(1320, 1015)

        self.root.bind("<Control-w>", self.quit)
        self.root.bind("<Escape>", self.quit)

        self.root.bind("<Up>", lambda _event: self.move_point_in_dir("<Up>"))
        self.root.bind("<Down>", lambda _event: self.move_point_in_dir("<Down>"))
        self.root.bind("<Left>", lambda _event: self.move_point_in_dir("<Left>"))
        self.root.bind("<Right>", lambda _event: self.move_point_in_dir("<Right>"))

        self.root.bind("<Motion>", self.set_coords_to_show)

        # Help window
        self.help_window = None

        # Control point pos
        self.control_point_pos_window = None

        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame (canvas)
        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas
        self.canvas = tk.Canvas(self.left_frame, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        self.canvas.bind("<Configure>", self.resize)

        # Allowing the user to drag and select the control points
        self.movable_point_info = MoveablePointInfo()

        self.canvas.bind("<Button-1>", self.control_point_left_click)
        self.canvas.bind("<B1-Motion>", self.control_point_left_click_drag)
        self.canvas.bind("<ButtonRelease-1>", self.control_point_left_click_release)
        self.canvas.bind("<Button-3>", self.control_point_right_click)

        self.mouse_in_canvas = False
        self.canvas.bind("<Enter>", self.mouse_entered_canvas)
        self.canvas.bind("<Leave>", self.mouse_left_canvas)

        self.control_pressed = False
        self.shift_pressed = False
        self.root.bind("<KeyPress>", self.track_special_key_press)
        self.root.bind("<KeyRelease>", self.track_special_key_release)

        self.root.bind("<Button-1>", self.entire_window_left_or_right_click)
        self.root.bind("<Button-3>", self.entire_window_left_or_right_click)

        # Right frame (controls)
        self.right_frame = tk.Frame(self.main_frame, width=200, padx=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Controls
        tk.Label(self.right_frame, text="Controls", font=("Arial", 12, "bold")).pack(pady=10)

        # Grid settings
        self.grid_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.grid_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.grid_settings_frame,
            text="Grid settings",
            font=("Arial", 12, "bold"),
            bg="gray75",
        ).pack(padx=5, pady=5)

        self.left_grid_settings_frame = tk.Frame(self.grid_settings_frame, bg="gray75")
        self.left_grid_settings_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_grid_settings_frame = tk.Frame(self.grid_settings_frame, bg="gray75")
        self.right_grid_settings_frame.pack(side=tk.RIGHT, fill=tk.Y)

        #   Toggle grid
        self.show_grid_var = tk.BooleanVar()
        self.show_grid_checkbox = tk.Checkbutton(
            self.left_grid_settings_frame,
            text="Show grid",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_grid_var,
            command=self.draw,
        )
        self.show_grid_checkbox.pack(fill=tk.X, pady=5)
        self.show_grid_var.set(True)

        #   Toggle axes
        self.show_axes_var = tk.BooleanVar()
        self.show_axes_checkbox = tk.Checkbutton(
            self.left_grid_settings_frame,
            text="Show axes",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_axes_var,
            command=self.draw,
        )
        self.show_axes_checkbox.pack(fill=tk.X, pady=5)
        self.show_axes_var.set(True)

        #   Toggle mouse coords
        self.show_coords_var = tk.BooleanVar()
        self.show_coords_checkbox = tk.Checkbutton(
            self.left_grid_settings_frame,
            text="Show coords",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_coords_var,
            command=self.draw,
        )
        self.show_coords_checkbox.pack(fill=tk.X, padx=5, pady=5)

        self.coords_to_show = (0, 0)

        #   Grid cell size
        self.grid_cell_size = 50
        self.grid_cell_size_var, self.grid_cell_size_spinbox, self.grid_cell_size_confirm = create_number_input(
            self.right_grid_settings_frame,
            "Grid cell size",
            25,
            500,
            increment=25,
            font_size=11,
            command=self.set_grid_cell_size,
        )
        self.grid_cell_size_var.set(self.grid_cell_size)

        # Control point settings
        self.control_point_settings_frame = tk.Frame(self.right_frame, bg="gray75")
        self.control_point_settings_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.control_point_settings_frame,
            text="Control point settings",
            font=("Arial", 12, "bold"),
            bg="gray75",
        ).pack(padx=5, pady=5)

        self.left_control_point_settings_frame = tk.Frame(self.control_point_settings_frame, bg="gray75")
        self.left_control_point_settings_frame.pack(fill=tk.Y, pady=5, side=tk.LEFT)

        self.right_control_point_settings_frame = tk.Frame(self.control_point_settings_frame, bg="gray75")
        self.right_control_point_settings_frame.pack(fill=tk.Y, pady=5, side=tk.RIGHT)

        #   Snapping interval
        tk.Label(self.left_control_point_settings_frame, text="Snapping interval", font=("Arial", 11), bg="gray75").pack(
            padx=5, pady=5
        )
        self.snapping_intervals = ["1", "1/2", "1/3", "1/4", "1/5"]
        self.snapping_intervals_selection = tk.StringVar()
        self.snapping_intervals_selection.set(self.snapping_intervals[1])
        self.snapping_intervals_dropdown = tk.OptionMenu(
            self.left_control_point_settings_frame, self.snapping_intervals_selection, *self.snapping_intervals
        )
        self.snapping_intervals_dropdown.pack(pady=5)

        #   Amount to shift w/ arrow keys
        self.shift_amount = 0.25
        self.shift_amount_var, self.shift_amount_spinbox, self.shift_amount_confirm = create_number_input(
            self.left_control_point_settings_frame,
            "Shift amount",
            0,
            1,
            increment=0.1,
            font_size=11,
            command=self.set_shift_amount,
            use_float=True,
        )
        self.shift_amount_var.set(self.shift_amount)

        #   Control point pos randomizer
        self.control_point_position_randomizer_button = tk.Button(
            self.left_control_point_settings_frame,
            text="Randomize control\npoint positions",
            command=lambda: run_funcs(self.randomize_control_point_pos, self.draw_bezier_curve, self.draw_control_points),
        )
        self.control_point_position_randomizer_button.pack(fill=tk.X, padx=5, pady=5)

        #   Setting to hide control points
        self.show_control_points_var = tk.BooleanVar()
        self.show_control_points_checkbox = tk.Checkbutton(
            self.left_control_point_settings_frame,
            text="Show control points",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_control_points_var,
            command=self.draw_control_points,
        )
        self.show_control_points_checkbox.pack(fill=tk.X, pady=5)
        self.show_control_points_var.set(True)

        #   Num control points
        self.num_control_points = 4
        self.num_control_points_var, self.num_control_points_spinbox, self.num_control_points_confirm = create_number_input(
            self.right_control_point_settings_frame,
            "Num control points",
            2,
            10,
            font_size=11,
            command=self.set_num_control_points,
        )
        self.num_control_points_var.set(self.num_control_points)

        self.control_points = [
            np.array([-2, 0]),
            np.array([-1.75, 2]),
            np.array([1.75, 2]),
            np.array([2, 0]),
        ]

        #   Control point radius
        self.control_point_radius = 7
        self.control_point_radius_var, self.control_point_radius_spinbox, self.control_point_radius_confirm = (
            create_number_input(
                self.right_control_point_settings_frame,
                "Control point radius",
                1,
                30,
                font_size=11,
                command=self.set_control_point_radius,
                use_float=True,
            )
        )
        self.control_point_radius_var.set(self.control_point_radius)

        #   Button to show all control point pos TODO
        self.control_point_position_list_button = tk.Button(
            self.right_control_point_settings_frame,
            text="Show all control\npoint positions",
            command=self.open_control_point_pos_list,
        )
        self.control_point_position_list_button.pack(fill=tk.X, padx=5, pady=5)

        #   Show lines between control points
        self.show_control_lines_var = tk.BooleanVar()
        self.show_control_lines_checkbox = tk.Checkbutton(
            self.right_control_point_settings_frame,
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

        #   Sample point radius
        self.sample_point_radius = 5
        self.sample_point_radius_var, self.sample_point_radius_spinbox, self.sample_point_radius_confirm = (
            create_number_input(
                self.left_bezier_settings_frame,
                "Sample point radius",
                1,
                20,
                font_size=11,
                command=self.set_sample_point_radius,
                use_float=True,
            )
        )
        self.sample_point_radius_var.set(self.sample_point_radius)

        #   Curve linewidth
        self.curve_linewidth = 2
        self.curve_linewidth_var, self.curve_linewidth_spinbox, self.curve_linewidth_confirm = create_number_input(
            self.left_bezier_settings_frame, "Curve linewidth", 1, 10, font_size=11, command=self.set_curve_linewidth
        )
        self.curve_linewidth_var.set(self.curve_linewidth)

        #   Curve resolution
        self.curve_resolution = 5
        self.resolution_var, self.resolution_spinbox, self.resolution_confirm = create_number_input(
            self.right_bezier_settings_frame, "Curve resolution", 1, 300, font_size=11, command=self.set_curve_resolution
        )
        self.resolution_var.set(self.curve_resolution)

        #   Show sampled points
        self.show_sampled_points_var = tk.BooleanVar()
        self.show_sampled_points_checkbox = tk.Checkbutton(
            self.right_bezier_settings_frame,
            text="Show sampled points",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_sampled_points_var,
            command=lambda: run_funcs(self.draw_bezier_curve, self.draw_control_points),
        )
        self.show_sampled_points_checkbox.pack(fill=tk.X, pady=5)

        #   Show bezier curve
        self.show_bezier_curve_var = tk.BooleanVar()
        self.show_bezier_curve_checkbox = tk.Checkbutton(
            self.right_bezier_settings_frame,
            text="Show Bezier curve",
            bg="gray75",
            activebackground="gray75",
            variable=self.show_bezier_curve_var,
            command=lambda: run_funcs(self.draw_bezier_curve, self.draw_control_points),
        )
        self.show_bezier_curve_checkbox.pack(fill=tk.X, pady=5)
        self.show_bezier_curve_var.set(True)

        # Help view
        self.help_frame = tk.Frame(self.right_frame, bg="gray75")
        self.help_frame.pack(fill=tk.X, pady=5)
        tk.Label(
            self.help_frame,
            text="Help",
            font=("Arial", 12, "bold"),
            bg="gray75",
        ).pack(padx=5, pady=5)

        #   Help selection
        help_sections = [
            "Quick start",
            "Help guides",
            "Grid settings",
            "Control point settings",
            "Bezier curve settings",
            "Controls",
            "Shortcuts",
            "Usage",
        ]
        self.help_selection = tk.StringVar()
        self.help_selection.set(help_sections[0])
        self.help_dropdown = tk.OptionMenu(self.help_frame, self.help_selection, *help_sections)
        self.help_dropdown.pack(fill=tk.X, padx=5, pady=5)

        #   Help open button
        self.help_open_button = tk.Button(self.help_frame, text="Open guide", command=self.open_help_guide)
        self.help_open_button.pack(fill=tk.X, padx=5, pady=5)

        # Reset button
        btn_reset = tk.Button(self.right_frame, text="Reset", command=self.reset)
        btn_reset.pack(fill=tk.X, pady=5)

        # Quit button
        btn_quit = tk.Button(self.right_frame, text="Quit", command=self.quit)
        btn_quit.pack(fill=tk.X, pady=5)

    def randomize_control_point_pos(self) -> None:
        xy_range = self.get_int_coord_limits()

        for i in range(len(self.control_points)):
            random_x = random.uniform(xy_range[0][0], xy_range[0][1])
            random_y = random.uniform(xy_range[1][0], xy_range[1][1])

            self.control_points[i] = np.array([random_x, random_y])

    def set_coords_to_show(self, event: tk.Event | None = None) -> None:
        if self.movable_point_info.point_idx == None:
            self.coords_to_show = self.canvas_to_coord((event.x, event.y))

        self.draw_coords()

    def mouse_entered_canvas(self, _event=None) -> None:
        self.mouse_in_canvas = True
        self.draw_coords()

    def mouse_left_canvas(self, _event=None) -> None:
        self.mouse_in_canvas = False
        self.draw_coords()

    def move_point_in_dir(self, dir: Literal["<Up>", "<Down>", "<Left>", "<Right>"]) -> None:
        if self.movable_point_info.mode != "select":
            return

        dir_str_to_vector = {
            "<Up>": np.array([0, 1]),
            "<Down>": np.array([0, -1]),
            "<Left>": np.array([-1, 0]),
            "<Right>": np.array([1, 0]),
        }

        self.control_points[self.movable_point_info.point_idx] += self.shift_amount * dir_str_to_vector[dir]

        xy_range = self.get_graph_coord_limits()
        limited_x = min(max(self.control_points[self.movable_point_info.point_idx][0], xy_range[0][0]), xy_range[0][1])
        limited_y = min(max(self.control_points[self.movable_point_info.point_idx][1], xy_range[1][0]), xy_range[1][1])
        self.control_points[self.movable_point_info.point_idx] = np.array([limited_x, limited_y])

        self.coords_to_show = tuple(np.round(self.control_points[self.movable_point_info.point_idx], COORD_DECIMAL_ROUNDING))

        self.draw_coords()
        self.draw_bezier_curve()
        self.draw_control_points()

    def entire_window_left_or_right_click(self, event: tk.Event | None = None) -> None:
        if self.mouse_in_canvas:
            return

        self.movable_point_info.reset()

        self.draw_coords()
        self.draw_control_points()

    def control_point_left_click(self, event: tk.Event | None = None) -> None:
        self.movable_point_info.reset()

        point_idx = self.get_point_hovered_over((event.x, event.y))

        if point_idx != -1:
            self.coords_to_show = self.control_points[point_idx]

            self.movable_point_info.set_og_point_coord(self.control_points[point_idx])
            self.movable_point_info.set_og_mouse_coord(self.canvas_to_coord((event.x, event.y)))
            self.movable_point_info.set_point_idx(point_idx)
            self.movable_point_info.set_mode("drag")

        self.draw_coords()
        self.draw_control_points()

    def control_point_left_click_drag(self, event: tk.Event | None = None) -> None:
        if self.movable_point_info.mode != "drag":
            return

        self.control_points[self.movable_point_info.point_idx] = self.process_new_point_coord(
            *self.movable_point_info.get_og_point_coord_and_mouse_movement(self.canvas_to_coord((event.x, event.y)))
        )

        xy_range = self.get_graph_coord_limits()
        limited_x = min(max(self.control_points[self.movable_point_info.point_idx][0], xy_range[0][0]), xy_range[0][1])
        limited_y = min(max(self.control_points[self.movable_point_info.point_idx][1], xy_range[1][0]), xy_range[1][1])
        self.control_points[self.movable_point_info.point_idx] = np.array([limited_x, limited_y])

        self.coords_to_show = tuple(np.round(self.control_points[self.movable_point_info.point_idx], COORD_DECIMAL_ROUNDING))

        self.draw_bezier_curve()
        self.draw_control_points()

    def control_point_left_click_release(self, event: tk.Event | None = None) -> None:
        self.movable_point_info.reset()
        self.coords_to_show = self.canvas_to_coord((event.x, event.y))

        self.draw_coords()
        self.draw_bezier_curve()
        self.draw_control_points()

    def control_point_right_click(self, event: tk.Event | None = None) -> None:
        point_idx = self.get_point_hovered_over((event.x, event.y))

        if not (point_idx == -1 or self.movable_point_info.mode == "drag"):
            if point_idx == self.movable_point_info.point_idx:
                self.movable_point_info.reset()
            elif self.movable_point_info.mode in [None, "select"]:
                self.coords_to_show = self.control_points[point_idx]

                self.movable_point_info.set_mode("select")
                self.movable_point_info.set_point_idx(point_idx)
        elif point_idx == -1:
            self.movable_point_info.reset()

        self.draw_coords()
        self.draw_control_points()

    def get_point_hovered_over(self, mouse_coord: tuple[float, float] | np.ndarray) -> int:
        point_idx = -1
        smallest_dist = float("inf")

        for i in range(len(self.control_points)):
            point = self.control_points[i]

            is_in_area, dist = in_circle_area(*mouse_coord, *self.coord_to_canvas(point), self.control_point_radius)

            if is_in_area and dist < smallest_dist:
                point_idx = i
                smallest_dist = dist

        return point_idx

    def track_special_key_press(self, event: tk.Event | None = None) -> None:
        self.control_pressed = self.key_press_logic(event, "Control", self.control_pressed)
        self.shift_pressed = self.key_press_logic(event, "Shift", self.shift_pressed)

    def key_press_logic(self, event: tk.Event, key: str, current_key_state: bool) -> bool:
        if key in event.keysym and not current_key_state:
            return True

        return current_key_state

    def track_special_key_release(self, event: tk.Event | None = None) -> None:
        self.control_pressed = self.key_release_logic(event, "Control", self.control_pressed)
        self.shift_pressed = self.key_release_logic(event, "Shift", self.shift_pressed)

    def key_release_logic(self, event: tk.Event, key: str, current_key_state: bool) -> bool:
        if key in event.keysym and current_key_state:
            return False

        return current_key_state

    def process_new_point_coord(self, og_point_coord: np.ndarray, og_mouse_movement: np.ndarray) -> np.ndarray:
        mouse_movement = og_mouse_movement.copy()

        if self.shift_pressed:
            moved_x = abs(og_mouse_movement[0]) > abs(og_mouse_movement[1])
            if moved_x:
                mouse_movement[1] = 0
            else:
                mouse_movement[0] = 0

        if self.control_pressed:
            snapping_interval_fraction = Fraction(self.snapping_intervals_selection.get())
            return (
                np.round(((og_point_coord + mouse_movement) / snapping_interval_fraction).astype(float))
                * snapping_interval_fraction
            ).astype(float)

        return og_point_coord + mouse_movement

    def set_shift_amount(self, _event=None) -> None:
        if not self.num_submission(self.shift_amount_spinbox, "shift amount", True):
            return

        self.shift_amount = self.limit_to_spinbox_range(self.shift_amount_spinbox, self.shift_amount_var.get())
        self.shift_amount = (
            int(self.shift_amount) if abs(int(self.shift_amount) - self.shift_amount) <= 1e-5 else self.shift_amount
        )
        self.shift_amount_var.set(self.shift_amount)

        self.draw_control_points()

    def set_grid_cell_size(self, _event=None) -> None:
        if not self.num_submission(self.grid_cell_size_spinbox, "grid cell size"):
            return

        self.grid_cell_size = int(self.limit_to_spinbox_range(self.grid_cell_size_spinbox, self.grid_cell_size_var.get()))
        self.grid_cell_size_var.set(self.grid_cell_size)

        self.draw()

    def set_num_control_points(self, _event=None) -> None:
        if not self.num_submission(self.num_control_points_spinbox, "number of control points"):
            return

        if self.num_control_points_var.get() - self.num_control_points > 1:
            messagebox.showerror(
                "number of control points error", "When increasing the number of control points, it must be done one by one"
            )
            self.num_control_points_var.set(self.num_control_points)
            return

        self.num_control_points = int(
            self.limit_to_spinbox_range(self.num_control_points_spinbox, self.num_control_points_var.get())
        )
        self.num_control_points_var.set(self.num_control_points)

        # Remove points
        while len(self.control_points) > self.num_control_points:
            self.control_points.pop()

        # Add points
        if len(self.control_points) < self.num_control_points:
            xy_range = self.get_int_coord_limits(self.grid_cell_size // 2)
            new_coord = np.array([xy_range[0][0], xy_range[1][1]])

            if coord_in_list(new_coord, self.control_points):
                messagebox.showerror("number of control points error", "First move the new control point out of the way")
                self.num_control_points -= 1
                self.num_control_points_var.set(self.num_control_points)
                return

            self.control_points.append(new_coord)

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_control_point_radius(self, _event=None) -> None:
        if not self.num_submission(self.control_point_radius_spinbox, "size of control points", True):
            return

        self.control_point_radius = self.limit_to_spinbox_range(
            self.control_point_radius_spinbox, self.control_point_radius_var.get()
        )
        self.control_point_radius = (
            int(self.control_point_radius)
            if abs(int(self.control_point_radius) - self.control_point_radius) <= 1e-5
            else self.control_point_radius
        )
        self.control_point_radius_var.set(self.control_point_radius)

        self.draw_control_points()

    def set_curve_resolution(self, _event=None) -> None:
        if not self.num_submission(self.resolution_spinbox, "resolution"):
            return

        self.curve_resolution = int(self.limit_to_spinbox_range(self.resolution_spinbox, self.resolution_var.get()))
        self.resolution_var.set(self.curve_resolution)

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_sample_point_radius(self, _event=None) -> None:
        if not self.num_submission(self.sample_point_radius_spinbox, "number of control points", True):
            return

        self.sample_point_radius = self.limit_to_spinbox_range(
            self.sample_point_radius_spinbox, self.sample_point_radius_var.get()
        )
        self.sample_point_radius = (
            int(self.sample_point_radius)
            if abs(int(self.sample_point_radius) - self.sample_point_radius) <= 1e-5
            else self.sample_point_radius
        )
        self.sample_point_radius_var.set(self.sample_point_radius)

        self.draw_bezier_curve()
        self.draw_control_points()

    def set_curve_linewidth(self, _event=None) -> None:
        if not self.num_submission(self.curve_linewidth_spinbox, "curve linewidth", True):
            return

        self.curve_linewidth = self.limit_to_spinbox_range(self.curve_linewidth_spinbox, self.curve_linewidth_var.get())
        self.curve_linewidth = (
            int(self.curve_linewidth)
            if abs(int(self.curve_linewidth) - self.curve_linewidth) <= 1e-5
            else self.curve_linewidth
        )
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
                f"{var_name} error",
                f"The {var_name} MUST be an {"int" if not allow_float else "float"} without letters, not '{spinbox.get()}'",
            )
            return False

        return True

    def get_graph_coord_limits(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Gets the range for the x coordinate in the graph, as well as the y coord
        The output is formatted like tuple[x_range, y_range], where the range is the smaller number then bigger number
        """
        low_x, high_y = self.canvas_to_coord((0, 0))
        high_x, low_y = self.canvas_to_coord((self.canvas.winfo_width(), self.canvas.winfo_height()))

        return ((low_x, high_x), (low_y, high_y))

    def get_int_coord_limits(self, offset: float | int = 0) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Gets the range for the x coordinate in the graph, as well as the y coord, where those ranges are at whole numbers
        The output is formatted like tuple[x_range, y_range], where the range is the smaller number then bigger number
        """
        middle_w = self.canvas.winfo_width() // 2 + 1
        middle_h = self.canvas.winfo_height() // 2 + 1

        canvas_x = (middle_w - offset) % self.grid_cell_size + offset
        canvas_y = (middle_h - offset) % self.grid_cell_size + offset

        low_x, high_y = self.canvas_to_coord((canvas_x, canvas_y))

        return ((low_x, -low_x), (-high_y, high_y))

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

    def draw(self, _event=None) -> None:
        self.draw_grid()
        self.draw_coords()
        self.draw_bezier_curve()
        self.draw_control_points()

    def draw_grid(self, _event=None) -> None:
        self.canvas.delete("grid_line")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        middle_w = width // 2 + 1
        middle_h = height // 2 + 1

        # Draw grid
        if self.show_grid_var.get():
            for i in range(middle_w, width, self.grid_cell_size):
                self.canvas.create_line(i, 0, i, height, tag="grid_line", fill="lightgray")
            for i in range(middle_w, -1, -self.grid_cell_size):
                self.canvas.create_line(i, 0, i, height, tag="grid_line", fill="lightgray")

            for i in range(middle_h, height, self.grid_cell_size):
                self.canvas.create_line(0, i, width, i, tag="grid_line", fill="lightgray")
            for i in range(middle_h, -1, -self.grid_cell_size):
                self.canvas.create_line(0, i, width, i, tag="grid_line", fill="lightgray")

        # Draw axis lines
        if self.show_axes_var.get():
            self.canvas.create_line(middle_w, 0, middle_w, height, tag="grid_line", fill="black", width=2)
            self.canvas.create_line(0, middle_h, width, middle_h, tag="grid_line", fill="black", width=2)

    def draw_coords(self, _event=None) -> None:
        self.canvas.delete("mouse_coords")

        if not self.show_coords_var.get():
            return

        mouse_coord_font = Font(family="Arial", size=15)
        mouse_coord_str_template = "({}, {})"
        if self.mouse_in_canvas or self.movable_point_info.point_idx != None:
            str_coords_to_show = []

            for coord in self.coords_to_show:
                str_coords_to_show.append(f"{coord:.2f}")

            mouse_coord_str = mouse_coord_str_template.format(*str_coords_to_show)
        else:
            mouse_coord_str = mouse_coord_str_template.format("-", "-")

        line_height = mouse_coord_font.metrics("linespace")

        pad_x = 5
        pad_y = 5

        xy_range = self.get_int_coord_limits(0)
        text_x, text_y = self.coord_to_canvas((xy_range[0][1], xy_range[1][0]))
        text_x -= pad_x
        text_y -= pad_y

        self.canvas.create_text(
            text_x,
            text_y - line_height / 2,
            text=mouse_coord_str,
            font=mouse_coord_font,
            anchor="e",
            fill="black",
            tags="mouse_coords",
        )

    def draw_control_points(self) -> None:
        self.canvas.delete("control_points")

        if not self.show_control_points_var.get():
            return

        if self.show_control_lines_var.get():
            for i in range(len(self.control_points) - 1):
                p1 = self.control_points[i]
                p2 = self.control_points[i + 1]

                self.canvas.create_line(
                    *self.coord_to_canvas(p1),
                    *self.coord_to_canvas(p2),
                    fill="gray55",
                    width=2,
                    tags="control_points",
                    dash=(5, 2),
                )

        for i in range(len(self.control_points)):
            control_point = self.control_points[i]
            fill_color = (
                self.colors["selected_control_point"]
                if i == self.movable_point_info.point_idx
                else self.colors["control_points"]
            )
            draw_circle(
                self.canvas,
                *self.coord_to_canvas(control_point),
                self.control_point_radius,
                fill=fill_color,
                tags="control_points",
            )

    def draw_bezier_curve(self) -> None:
        self.canvas.delete("bezier_curve")

        if not self.show_bezier_curve_var.get():
            return

        bezier_curve_points = get_bezier_curve_points(self.control_points, int(self.curve_resolution))

        for i in range(len(bezier_curve_points) - 1):
            p1 = bezier_curve_points[i]
            p2 = bezier_curve_points[i + 1]

            self.canvas.create_line(
                *self.coord_to_canvas(p1),
                *self.coord_to_canvas(p2),
                fill=self.colors["curve"],
                width=self.curve_linewidth,
                tags="bezier_curve",
            )

            if i != 0:
                draw_circle(
                    self.canvas,
                    *self.coord_to_canvas(p1),
                    self.curve_linewidth // 2,
                    fill=self.colors["curve"],
                    outline=self.colors["curve"],
                    tags="bezier_curve",
                )

        if self.show_sampled_points_var.get():
            for i in range(1, len(bezier_curve_points) - 1):
                point = bezier_curve_points[i]
                draw_circle(
                    self.canvas,
                    *self.coord_to_canvas(point),
                    self.sample_point_radius,
                    fill=self.colors["sampled_points"],
                    tags="bezier_curve",
                )

    def open_control_point_pos_list(self) -> None:  # TODO
        messagebox.showinfo(
            "Feature coming soon",
            """
                This feature will come soon
                I still need to write out all the docs
            """,
        )
        
        # self.control_point_pos_window = create_popup_window_toplevel(
        #     self.root,
        #     "Control point positions",
        #     self.quit,
        # )

        # show_control_point_pos_in_window(
        #     self.control_point_pos_window,
        #     self.control_points,
        #     ("Arial", 11),
        # )

    def open_help_guide(self) -> None:  # TODO
        messagebox.showinfo(
            "Feature coming soon",
            """
                This feature will come soon
                I still need to write out all the docs
            """,
        )
        # # New window + scolling text test
        # self.help_window = tk.Toplevel(self.root)
        # self.help_window.title("Test msg")
        # self.help_window.protocol("WM_DELETE_WINDOW", self.quit)
        # # new_window.geometry("300x200")

        # scrollbar = tk.Scrollbar(self.help_window)
        # scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # text_area = tk.Text(self.help_window, font=("Arial", 11), wrap=tk.WORD, yscrollcommand=scrollbar.set)
        # text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # scrollbar.config(command=text_area.yview)

        # text_area.insert(tk.END,
        # """
        #     Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras tincidunt risus in hendrerit gravida. Suspendisse vitae mi id nulla facilisis pretium at vel enim. Curabitur mattis urna sed elementum molestie.
        #     Interdum et malesuada fames ac ante ipsum primis in faucibus. Vestibulum id libero a orci cursus accumsan et in neque. Nulla in mauris quam. Fusce fermentum pharetra lectus, id tincidunt risus dictum eget.
        #     Proin tempus tincidunt scelerisque. Sed gravida tortor efficitur tortor tincidunt, eu faucibus nulla facilisis. Suspendisse eu nulla et leo efficitur porttitor ac varius quam. Mauris a sagittis quam.
        #     Quisque vitae quam vestibulum, facilisis justo et, blandit enim. Aliquam erat volutpat. Nulla semper, arcu ut imperdiet consectetur, urna dui tempor urna, eget mattis leo nisl eu turpis.
        #     Quisque in odio eu urna mattis elementum mattis ac magna.

        #     Curabitur efficitur nisl non laoreet luctus. Maecenas suscipit eros neque, non sagittis leo blandit vel. Etiam nec dolor ac lacus auctor consequat id nec felis.
        #     Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Aenean vel nibh quis urna faucibus scelerisque. Proin quam eros, pulvinar a tristique eget, posuere et urna.
        #     Nulla a nisi et ligula ultricies auctor et nec augue. Donec in urna non enim interdum iaculis. Donec fringilla maximus pellentesque. Maecenas semper aliquam orci eu varius.
        #     Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Phasellus facilisis venenatis eleifend. Pellentesque purus nisi, bibendum ac libero ac, consequat imperdiet quam.
        #     Pellentesque leo tellus, sodales at erat in, elementum ultrices velit. Integer non feugiat ex, egestas interdum ex. Nunc quam tellus, commodo sed tellus quis, aliquam faucibus sem.

        #     Nunc feugiat, velit non mollis imperdiet, tortor nunc malesuada lectus, eget porttitor lorem massa id turpis. Cras convallis libero nec urna venenatis, non malesuada ligula porttitor.
        #     Curabitur a tellus ac ex tempus porttitor sed in ipsum. Praesent tempus risus non tellus suscipit venenatis eu mattis nulla. Praesent sem est, pretium quis tempus ac, molestie id purus.
        #     Nunc rutrum tortor arcu, sit amet tincidunt nisl tincidunt vel. Cras malesuada malesuada pretium. Curabitur ut lacus metus. Integer erat felis, luctus a pulvinar et, egestas quis neque.
        #     Duis venenatis, felis nec volutpat tincidunt, augue purus dignissim turpis, at bibendum risus mi eget elit. Nam vel tellus sit amet arcu tempor interdum non faucibus ante. Sed in magna at ex vulputate maximus ut a nisi.
        #     Suspendisse aliquam enim vitae massa bibendum sollicitudin. Lorem ipsum dolor sit amet, consectetur adipiscing elit.

        #     Morbi iaculis ex scelerisque lacus dapibus posuere. Sed malesuada rutrum placerat. Vivamus lobortis ut sem a fermentum. Nulla tempus hendrerit ex in accumsan. Integer augue sapien, eleifend non nibh a, convallis iaculis est.
        #     Integer orci nisi, volutpat eleifend arcu egestas, volutpat condimentum sem. Morbi a orci facilisis, euismod purus ullamcorper, feugiat est. Maecenas accumsan magna sit amet odio efficitur finibus.
        #     Sed vel tellus pretium, venenatis ligula eu, scelerisque libero. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut nec aliquam velit, id commodo purus.
        #     Cras pretium lorem et laoreet convallis.

        #     Morbi malesuada quis mi non varius. Nulla commodo maximus lobortis. Curabitur in ex ut lorem maximus hendrerit. Duis id dolor lacus. Ut venenatis sodales nibh eu finibus. Aliquam erat volutpat.
        #     Sed placerat eros at gravida porttitor. Nunc nisi tortor, rhoncus a est in, ullamcorper semper lectus. Donec gravida, tortor id accumsan venenatis, arcu leo accumsan elit, nec ornare enim ipsum ac diam.
        #     In pellentesque quam odio, ac faucibus ex mattis sed. Mauris tellus orci, tristique nec arcu in, elementum sollicitudin dui. Aliquam eu est non magna suscipit varius a eu tellus. Quisque venenatis porta metus, quis laoreet ligula.
        #     Duis porta lectus quis commodo congue.
        # """
        # )

        # text_area.config(state="disabled")

        # print(f"Guide opened: {self.help_selection.get()}")

    def resize(self, _event=None) -> None:
        self.draw()

    def reset(self) -> None:
        # Grid settings
        #   Reset show grid, show axes, and show coords
        self.show_grid_var.set(True)
        self.show_axes_var.set(True)
        self.show_coords_var.set(False)

        #   Reset grid cell size
        self.grid_cell_size = 50
        self.grid_cell_size_var.set(self.grid_cell_size)

        # Control point settings
        #   Reset snapping interval
        self.snapping_intervals_selection.set(self.snapping_intervals[1])

        #   Reset shift amount
        self.shift_amount_var.set(0.25)

        #   Reset show control points
        self.show_control_points_var.set(True)

        #   Reset control points
        self.control_points = [
            np.array([-2, 0]),
            np.array([-1.75, 2]),
            np.array([1.75, 2]),
            np.array([2, 0]),
        ]

        self.num_control_points = 4
        self.num_control_points_var.set(self.num_control_points)

        #   Reset control point radius
        self.control_point_radius = 7
        self.control_point_radius_var.set(self.control_point_radius)

        #   Reset show lines between points option
        self.show_control_lines_var.set(False)

        # Bezier surve settings
        #   Reset sample point radius
        self.sample_point_radius = 5
        self.sample_point_radius_var.set(self.sample_point_radius)

        #   Reset curve linewidth
        self.curve_linewidth = 2
        self.curve_linewidth_var.set(self.curve_linewidth)

        #   Reset resolution
        self.curve_resolution = 5
        self.resolution_var.set(self.curve_resolution)

        #   Reset show sampled points
        self.show_sampled_points_var.set(False)

        #   Reset show Bezier curve
        self.show_bezier_curve_var.set(True)

        # Draw to show changes
        self.draw()

        if self.debug:
            print(self.root.winfo_width(), self.root.winfo_height())
            print(self.get_graph_coord_limits())

    def run_gui(self) -> None:
        self.root.mainloop()

    def quit(self, _event=None) -> None:
        if self.help_window is not None:
            self.help_window.destroy()
            self.help_window = None
        elif self.control_point_pos_window is not None:
            self.control_point_pos_window.destroy()
            self.control_point_pos_window = None
        else:
            self.root.destroy()


if __name__ == "__main__":
    bezier_gui = BezierGUI(debug=True)
    bezier_gui.run_gui()
