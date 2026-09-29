import numpy as np
import tkinter as tk
from tkinter_text_tag import tkinter_text_tag_formatter

TAB = "    "


def setup_control_point_pos_window(window: tk.Tk | tk.Toplevel, font: tuple[str, int] = ("Arial", 11)) -> tk.Text:
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area = tk.Text(
        window,
        font=font,
        wrap=tk.WORD,
        yscrollcommand=scrollbar.set,
        padx=10,
        pady=10,
    )
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_area.yview)
    text_area.config(state="disabled")

    return text_area


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
        text_lines.append(f"{TAB}({point[0]:.2f}, {point[1]:.2f}),")

    text_lines.append("]")

    tags = {
        "SUBSCRIPT": {
            "font": ("Arial", 8),
            "offset": -3,
        },
        "BOLD": {
            "font": ("Arial", 11, "bold"),
        },
    }

    tkinter_text_tag_formatter(text_area, "\n".join(text_lines), tags)


if __name__ == "__main__":
    root = tk.Tk()
    setup_control_point_pos_window(root, [])
    root.mainloop()
