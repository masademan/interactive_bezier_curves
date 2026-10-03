import random
import numpy as np
import tkinter as tk
from tkinter.font import Font
from tkinter import messagebox
from fractions import Fraction
from utils.utils import run_funcs
from typing import Callable, Literal
from help_guide.help_guide import HELP_SECTIONS
from tkinter_text_renderer.tkinter_text_renderer import clear_text_area
from bezier_curve.bezier_curve import get_bezier_curve_points
from interactive_displays.interactive_help_menu import show_help_guide_in_window
from interactive_displays.interactive_control_point_pos import show_control_point_pos_in_window
from interactive_displays.text_popup_window import (
    setup_text_popup_window,
    create_popup_window_toplevel,
    set_max_window_size_with_text,
    add_buttons_to_text_popup_window,
)

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
        self.root.bind("<Control-W>", self.full_quit)
        self.root.bind("<Escape>", self.quit)

        self.root.bind("<Up>", lambda _event: self.move_point_in_dir("<Up>"))
        self.root.bind("<Down>", lambda _event: self.move_point_in_dir("<Down>"))
        self.root.bind("<Left>", lambda _event: self.move_point_in_dir("<Left>"))
        self.root.bind("<Right>", lambda _event: self.move_point_in_dir("<Right>"))

        self.root.bind("<Motion>", self.set_coords_to_show)

        # Help window
        self.help_window = None
        self.help_text_area = None
        self.current_help_guide = None

        # Control point pos
        self.control_point_pos_window = None
        self.control_point_text_area = None

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
            20,
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

        #   Button to show all control point pos
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
        self.help_selection = tk.StringVar()
        self.help_selection.set(HELP_SECTIONS[0])
        self.help_dropdown = tk.OptionMenu(self.help_frame, self.help_selection, *HELP_SECTIONS)
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
        if not self.show_control_points_var.get():
            return -1

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

        if self.control_point_text_area is not None:
            clear_text_area(self.control_point_text_area)
            show_control_point_pos_in_window(self.control_point_text_area, self.control_points)

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

    def open_control_point_pos_list(self) -> None:
        if self.control_point_pos_window != None:
            messagebox.showinfo(
                "Control point pos",
                "A window showing the positions of the control points is already open",
            )
            self.control_point_pos_window.deiconify()
            self.control_point_pos_window.lift()
            self.control_point_pos_window.focus_force()
            return

        self.control_point_pos_window = create_popup_window_toplevel(
            self.root,
            "Control point positions",
            self.quit,
            full_quit_func=self.full_quit,
        )

        self.control_point_text_area = setup_text_popup_window(self.control_point_pos_window)

        clear_text_area(self.control_point_text_area)
        show_control_point_pos_in_window(self.control_point_text_area, self.control_points)

        self.control_point_pos_window.focus_force()

    def open_help_guide(self) -> None:
        if self.help_window != None:
            if self.current_help_guide == self.help_selection.get():
                messagebox.showinfo(
                    "Help guide",
                    f"A window showing the help guide for '{self.current_help_guide}' is already open",
                )
                self.help_window.deiconify()
                self.help_window.lift()
                self.help_window.focus_force()
                return

            self.help_window.destroy()
            self.help_text_area = None
            self.current_help_guide = None

        self.current_help_guide = self.help_selection.get()

        self.help_window = create_popup_window_toplevel(
            self.root,
            f"Help guide: {self.current_help_guide}",
            self.quit,
            full_quit_func=self.full_quit,
        )

        self.help_text_area = setup_text_popup_window(self.help_window)

        clear_text_area(self.help_text_area)
        show_help_guide_in_window(self.help_text_area, self.current_help_guide)

        help_guide_idx = HELP_SECTIONS.index(self.current_help_guide)
        buttons_to_add = []
        if help_guide_idx == 0:
            buttons_to_add.append((f"Next guide: {HELP_SECTIONS[help_guide_idx + 1]} >", self.next_help_guide, "right"))
        elif help_guide_idx == len(HELP_SECTIONS) - 1:
            buttons_to_add.append((f"< Prev guide: {HELP_SECTIONS[help_guide_idx - 1]}", self.prev_help_guide))
        else:
            buttons_to_add.append((f"< Prev guide: {HELP_SECTIONS[help_guide_idx - 1]}", self.prev_help_guide))
            buttons_to_add.append((f"Next guide: {HELP_SECTIONS[help_guide_idx + 1]} >", self.next_help_guide))

        add_buttons_to_text_popup_window(*buttons_to_add, text_area=self.help_text_area, button_to_text_spacing="\n")

        set_max_window_size_with_text(self.help_window, self.help_text_area)

        self.help_window.focus_force()

    def next_help_guide(self) -> None:
        if self.current_help_guide == None:
            messagebox.showerror(
                "Help guide error",
                "There has been a variable unsync. Close and reopen the program and try again.\n"
                "If the issue persists, contact the maintainer to fix the bug.",
            )
            return

        help_guide_idx = HELP_SECTIONS.index(self.current_help_guide)
        if help_guide_idx == len(HELP_SECTIONS) - 1:
            return

        self.help_selection.set(HELP_SECTIONS[help_guide_idx + 1])

        self.open_help_guide()

    def prev_help_guide(self) -> None:
        if self.current_help_guide == None:
            messagebox.showerror(
                "Help guide error",
                "There has been a variable unsync. Close and reopen the program and try again.\n"
                "If the issue persists, contact the maintainer to fix the bug.",
            )
            return

        help_guide_idx = HELP_SECTIONS.index(self.current_help_guide)
        if help_guide_idx == 0:
            return

        self.help_selection.set(HELP_SECTIONS[help_guide_idx - 1])

        self.open_help_guide()

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
            self.help_text_area = None
            self.current_help_guide = None
        elif self.control_point_pos_window is not None:
            self.control_point_pos_window.destroy()
            self.control_point_pos_window = None
            self.control_point_text_area = None
        else:
            self.root.destroy()

    def full_quit(self, _event=None) -> None:
        self.root.destroy()


if __name__ == "__main__":
    bezier_gui = BezierGUI(debug=True)
    bezier_gui.run_gui()
