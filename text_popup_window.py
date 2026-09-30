import tkinter as tk
from typing import Callable


def create_popup_window_toplevel(root: tk.Tk, title: str, quit_func: Callable, offset: float = 60) -> tk.Toplevel:
    popup_window = tk.Toplevel(root)
    popup_window.title(title)
    popup_window.geometry(f"+{root.winfo_x() + offset}+{root.winfo_y() + offset}")
    popup_window.protocol("WM_DELETE_WINDOW", quit_func)

    popup_window.bind("<Control-w>", quit_func)
    popup_window.bind("<Escape>", quit_func)

    return popup_window


def setup_text_popup_window(window: tk.Tk | tk.Toplevel, font: tuple[str, int] = ("Arial", 11)) -> tk.Text:
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


def resize_button_frame_in_popup_window(event: tk.Event, button_frame: tk.Frame, offset: float = 25, height: float = 40):
    button_frame.config(width=event.width - offset, height=height)


def forward_scroll_to_text(event: tk.Event, text_area: tk.Text):
    """Forwards scroll wheel events to the parent text area."""
    # Windows and macOS
    if hasattr(event, "delta") and event.delta != 0:
        direction = -1 if event.delta > 0 else 1
        text_area.yview_scroll(direction, "units")

    # Linux
    elif hasattr(event, "num"):
        if event.num == 4:
            text_area.yview_scroll(-1, "units")
        elif event.num == 5:
            text_area.yview_scroll(1, "units")


def enable_widget_scrolling(widget: tk.Widget, text_area: tk.Text):
    """Binds mouse scroll events on a widget to scroll the target text_area."""
    widget.bind("<MouseWheel>", lambda e: forward_scroll_to_text(e, text_area))
    widget.bind("<Button-4>", lambda e: forward_scroll_to_text(e, text_area))
    widget.bind("<Button-5>", lambda e: forward_scroll_to_text(e, text_area))


def add_buttons_to_text_popup_window(
    *button_data: tuple[tuple[str, Callable | None, str | None]], text_area: tk.Text, button_to_text_spacing: str = ""
) -> None:
    """
    *button_data is a tuple of tuples, each of which is composed of the text in a certain button and the function that
        it'll call when pressed, unless the "function" provided is None.
        The third item is the side to put the button on, which will revert to the default setting if set to None
    text_area is the tk.Text object that the button will be stored in
    button_to_text_spacing could be any string, but preferably it should only consist of a bunch of '\\n' characters
    """
    text_area_state = text_area.cget("state")
    text_area.config(state="normal")

    text_area.tag_config("window_center_align", justify="center")

    button_frame = tk.Frame(text_area, bg=text_area.cget("bg"))
    button_frame.pack_propagate(False)

    if len(button_data) >= 1:
        tk.Button(
            button_frame,
            text=button_data[0][0],
            command=button_data[0][1] if button_data[0][1] else "",
            padx=4,
            pady=2.5,
        ).pack(padx=5, side=tk.LEFT if len(button_data) == 2 or len(button_data[0]) < 3 else button_data[0][2])

    if len(button_data) == 2:
        tk.Button(
            button_frame,
            text=button_data[1][0],
            command=button_data[1][1] if button_data[1][1] else "",
            padx=4,
            pady=2.5,
        ).pack(padx=5, side=tk.RIGHT)
    elif len(button_data) > 2:
        for current_button_data in button_data:
            tk.Button(
                button_frame,
                text=current_button_data[0],
                command=current_button_data[1] if current_button_data[1] else "",
                padx=4,
                pady=2.5,
            ).pack(padx=5, side=tk.LEFT if len(current_button_data) < 3 else current_button_data[2])
            
    enable_widget_scrolling(button_frame, text_area)
    for child in button_frame.winfo_children():
        enable_widget_scrolling(child, text_area)

    text_area.insert(tk.END, button_to_text_spacing)

    text_area.bind("<Configure>", lambda event: resize_button_frame_in_popup_window(event, button_frame, 25, 40))

    start_idx = text_area.index(tk.END)
    text_area.window_create(tk.END, window=button_frame)
    text_area.tag_add("window_center_align", start_idx, tk.END)

    text_area.config(state=text_area_state)
