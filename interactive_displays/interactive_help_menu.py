import tkinter as tk
from help_guide.help_guide import HELP_GUIDE_SELECTION
from tkinter_text_renderer.tkinter_text_renderer import tkinter_text_tag_formatter


def show_help_guide_in_window(text_area: tk.Text, guide_selected: str) -> None:
    text_area.config(state="normal")

    guide_data = HELP_GUIDE_SELECTION[guide_selected]
    tkinter_text_tag_formatter(text_area, guide_data["text"], guide_data["tags"], guide_data["codes"])

    text_area.config(state="disabled")
