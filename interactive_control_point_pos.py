import numpy as np
import tkinter as tk
from tkinter_text_tag import tkinter_text_tag_formatter


def show_control_point_pos_in_window(text_area: tk.Text, control_points: list[np.ndarray]) -> None:
    # Where the control point positions are turned into a string representation
    text_lines = []

    #   P[i]: ([x], [y])
    text_lines.append("[BOLD]P[SUBSCRIPT]i[SUBSCRIPT/]: (x, y)[BOLD/]")
    for i in range(len(control_points)):
        point = control_points[i]

        text_lines.append(f"P[SUBSCRIPT]{i + 1}[SUBSCRIPT/]: ({point[0]:.2f}, {point[1]:.2f})")

    #   [
    #       (x1, y1),
    #       (x2, y2),
    #   ]
    text_lines.append("\nList form:")
    text_lines.append("[")

    for point in control_points:
        text_lines.append(f"[/TAB]({point[0]:.2f}, {point[1]:.2f}),")

    text_lines.append("]")

    formatting_tags = {
        "SUBSCRIPT": {
            "font": ("Arial", 8),
            "offset": -3,
        },
        "BOLD": {
            "font": ("Arial", 11, "bold"),
        },
    }

    text_codes = {
        "TAB": "    "
    }

    tkinter_text_tag_formatter(
        text_area,
        "\n".join(text_lines),
        formatting_tags=formatting_tags,
        text_codes=text_codes,
        show_warnings_only_in_window=True,
    )
