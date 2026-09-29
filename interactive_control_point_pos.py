import numpy as np
import tkinter as tk


def show_control_point_pos_in_window(
    window: tk.Tk | tk.Toplevel, control_points: list[np.ndarray], font: tuple[str, int] = ("Arial", 11)
):
    scrollbar = tk.Scrollbar(window)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    text_area = tk.Text(window, font=font, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    root.mainloop()
