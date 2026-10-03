import tkinter as tk
from tkinter_text_renderer.tkinter_text_renderer import tkinter_text_tag_formatter


def show_help_guide_in_window(text_area: tk.Text, guide_selected: str) -> None:  # TODO
    text_lines = []

    text_area.config(state="normal")
    text_area.config(state="normal")
    long_text = f"Current guide: {guide_selected}\n" + "Scroll down to see the button.\n\n" + ("Line of text...\n" * 40)
    text_area.insert(tk.END, long_text)
    text_area.config(state="disabled")

    # tkinter_text_tag_formatter(text_area, "\n".join(text_lines), tags)
