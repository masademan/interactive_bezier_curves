import tkinter as tk
from help_guide.help_guide import HELP_GUIDE_SELECTION
from tkinter_text_renderer.tkinter_text_renderer import tkinter_text_tag_formatter


def show_help_guide_in_window(text_area: tk.Text, guide_selected: str) -> None:
    text_area.config(state="normal")

    guide_data = HELP_GUIDE_SELECTION[guide_selected]
    if "text" not in guide_data:
        raise NotImplementedError(f"The text component in guide '{guide_selected}' has not yet been written")
    
    guide_text = guide_data["text"]
    guide_tags = guide_data.get("tags", HELP_GUIDE_SELECTION["default"]["tags"])
    guide_codes = guide_data.get("codes", HELP_GUIDE_SELECTION["default"]["codes"])
    tkinter_text_tag_formatter(text_area, guide_text, guide_tags, guide_codes)

    text_area.config(state="disabled")
