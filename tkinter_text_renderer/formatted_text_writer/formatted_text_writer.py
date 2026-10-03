import os
import re
import tkinter as tk
from typing import Literal, Any
from tkinter import filedialog, messagebox
from interactive_displays.text_popup_window import (
    setup_text_popup_window,
    create_popup_window_toplevel,
    set_max_window_size_with_text,
)
from tkinter_text_renderer.tkinter_text_renderer import (
    TEXT_CODE,
    OPENING_TAG,
    CLOSING_TAG,
    clear_text_area,
    tkinter_text_tag_formatter,
)

HELP_GUIDE_FOR_TEXT_WRITER = f""""""
TAGS_FOR_HELP_GUIDE = {
    "SUBSCRIPT": {
        "font": ("Arial", 8),
        "offset": -3,
    },
    "BOLD": {
        "font": ("Arial", 11, "bold"),
    },
}
CODES_FOR_HELP_GUIDE = {"TAB": "    "}


class FormattedTextWriter:
    def __init__(self, title="Formatted text", offset_x: float = 40, offset_y: float = 40):
        self.root = tk.Tk()
        self.root.title(title + " writer")
        self.title = title

        self.root.protocol("WM_DELETE_WINDOW", self.full_quit)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight() - 2 * offset_y
        self.root.geometry(
            f"{(self.screen_width - offset_x)//3 - offset_x}x{self.screen_height - 2*offset_y}+{offset_x}+{offset_y}"
        )

        self.root.bind("<Control-w>", self.quit)
        self.root.bind("<Control-W>", self.full_quit)
        self.root.bind("<Escape>", self.quit)

        self.saved_text_progress = True
        self.text_file_path = None

        # Setting up the main writing area
        self.root.config(bg="white")
        tk.Label(self.root, text="Write text here", font=("Arial", 12, "bold"), bg="white").pack(padx=5, pady=5)
        self.text_options_frame = tk.Frame(self.root, bg="white")
        self.text_options_frame.pack(fill=tk.X, padx=5, pady=5)
        self.text_options_frame.columnconfigure(0, weight=1)
        self.text_options_frame.columnconfigure(1, weight=1)
        self.text_options_frame.columnconfigure(2, weight=1)
        self.text_options_frame.columnconfigure(3, weight=1)

        self.load_text_button = tk.Button(
            self.text_options_frame,
            text="Load text",
            command=self.load_text,
        )
        self.load_text_button.grid(row=0, column=0, padx=5, pady=5)

        self.open_help_for_writer_button = tk.Button(
            self.text_options_frame,
            text="Help",
            command=self.open_help,
        )
        self.open_help_for_writer_button.grid(row=0, column=1, padx=5, pady=5)
        self.help_window = None

        self.clear_text_button = tk.Button(
            self.text_options_frame,
            text="Clear text",
        )
        self.clear_text_button.grid(row=0, column=2, padx=5, pady=5)

        self.copy_text_button = tk.Button(
            self.text_options_frame,
            text="Copy text",
        )
        self.copy_text_button.grid(row=0, column=3, padx=5, pady=5)

        self.text_text_area = setup_text_popup_window(self.root, undo=True)
        self.prev_text_text_content = tk.StringVar(value=self.get_text_area_content(self.text_text_area))
        self.copy_text_button.config(
            command=lambda: self.copy_txt_to_clipboard(
                repr(self.get_text_area_content(self.text_text_area))[1:-1],
            )
        )
        self.clear_text_button.config(command=lambda: self.clear_and_update(self.text_text_area))
        self.bind_text_box_stuff(self.text_text_area)
        self.text_text_area.config(state="normal")
        self.text_text_area.bind("<KeyRelease>", lambda _event: self.updated_text_area(idx=0))

        self.root.bind("<Control-Key-1>", lambda _event: self.load_text())
        self.root.bind("<Control-Key-2>", lambda _event: self.clear_and_update(self.text_text_area))

        # Setting up root values
        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Setting up where the formatting tags are defined
        self.tags_window = create_popup_window_toplevel(
            self.root,
            title + " formatting",
            self.quit,
            custom_geometry=f"{root_width}x{(self.screen_height - offset_y)//2 - offset_y}+{root_x + root_width + offset_x}+{root_y}",
            full_quit_func=self.full_quit,
        )
        self.tags_window.config(bg="white")
        tk.Label(
            self.tags_window,
            text="Formatting tags",
            font=("Arial", 12, "bold"),
            bg="white",
        ).pack(padx=5, pady=5)
        self.tags_settings_frame = tk.Frame(self.tags_window, bg="white")
        self.tags_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        self.tags_settings_frame.columnconfigure(0, weight=1)
        self.tags_settings_frame.columnconfigure(1, weight=1)
        self.tags_settings_frame.columnconfigure(2, weight=1)

        self.clear_tags_button = tk.Button(
            self.tags_settings_frame,
            text="Clear tags",
        )
        self.clear_tags_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_tags_button = tk.Button(
            self.tags_settings_frame,
            text="Update preview",
            command=self.update_preview,
        )
        self.update_tags_button.grid(row=0, column=1, padx=5, pady=5)

        self.copy_tags_button = tk.Button(
            self.tags_settings_frame,
            text="Convert tags and copy",
            command=lambda: self.copy_txt_to_clipboard(str(self.read_tags(force_read=True))),
        )
        self.copy_tags_button.grid(row=0, column=2, padx=5, pady=5)

        self.tags_text_area = setup_text_popup_window(self.tags_window, undo=True)
        self.prev_tags_text_content = tk.StringVar(value=self.get_text_area_content(self.tags_text_area))
        self.clear_tags_button.config(command=lambda: self.clear_and_update(self.tags_text_area))
        self.bind_text_box_stuff(self.tags_text_area)
        self.tags_text_area.config(state="normal")
        self.tags_text_area.bind("<KeyRelease>", lambda _event: self.updated_text_area(idx=1, update_preview=False))

        self.tags_window.bind("<Control-Key-1>", lambda _event: self.clear_and_update(self.tags_text_area))

        self.tags_window.update_idletasks()
        self.tags_window.focus_force()

        # Setting up where the text codes are defined
        self.codes_window = create_popup_window_toplevel(
            self.root,
            title + " codes",
            self.quit,
            custom_geometry=f"{root_width}x{(self.screen_height - offset_y)//2 - offset_y}+{root_x + root_width + offset_x}+{root_y + (self.screen_height - offset_y)//2}",
            full_quit_func=self.full_quit,
        )
        self.codes_window.config(bg="white")
        tk.Label(
            self.codes_window,
            text="Text codes",
            font=("Arial", 12, "bold"),
            bg="white",
        ).pack(padx=5, pady=5)
        self.codes_settings_frame = tk.Frame(self.codes_window, bg="white")
        self.codes_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        self.codes_settings_frame.columnconfigure(0, weight=1)
        self.codes_settings_frame.columnconfigure(1, weight=1)
        self.codes_settings_frame.columnconfigure(2, weight=1)

        self.clear_codes_button = tk.Button(
            self.codes_settings_frame,
            text="Clear tags",
        )
        self.clear_codes_button.grid(row=0, column=0, padx=5, pady=5)

        self.update_codes_button = tk.Button(
            self.codes_settings_frame,
            text="Update preview",
            command=self.update_preview,
        )
        self.update_codes_button.grid(row=0, column=1, padx=5, pady=5)

        self.copy_codes_button = tk.Button(
            self.codes_settings_frame,
            text="Convert codes and copy",
            command=lambda: self.copy_txt_to_clipboard(str(self.read_codes(force_read=True))),
        )
        self.copy_codes_button.grid(row=0, column=2, padx=5, pady=5)

        self.codes_text_area = setup_text_popup_window(self.codes_window, undo=True)
        self.prev_codes_text_content = tk.StringVar(value=self.get_text_area_content(self.codes_text_area))
        self.clear_codes_button.config(command=lambda: self.clear_and_update(self.codes_text_area))
        self.bind_text_box_stuff(self.codes_text_area)
        self.codes_text_area.config(state="normal")
        self.codes_text_area.bind("<KeyRelease>", lambda _event: self.updated_text_area(idx=2, update_preview=False))

        self.codes_window.bind("<Control-Key-1>", lambda _event: self.clear_and_update(self.codes_text_area))

        self.codes_window.update_idletasks()
        self.codes_window.focus_force()

        # Setting up where the preview is
        self.preview_window = create_popup_window_toplevel(
            self.root,
            title + " preview",
            self.quit,
            custom_geometry=f"{root_width}x{root_height}+{root_x + 2*root_width + 2*offset_x}+{root_y}",
            full_quit_func=self.full_quit,
        )
        self.preview_window.config(bg="white")

        #   Text preview settings
        tk.Label(self.preview_window, text="Text preview settings", font=("Arial", 12, "bold"), bg="white").pack(
            padx=5, pady=5
        )
        self.preview_settings_frame = tk.Frame(self.preview_window, bg="white")
        self.preview_settings_frame.pack(fill=tk.X, pady=5)
        self.preview_settings_frame.columnconfigure(0, weight=1)
        self.preview_settings_frame.columnconfigure(1, weight=1)
        self.preview_settings_frame.columnconfigure(2, weight=1)

        #       Text preview formatting toggle
        self.do_formatting_var = tk.BooleanVar(value=True)
        self.prev_do_formatting = tk.BooleanVar(value=self.do_formatting_var.get())
        self.do_formatting_checkbox = tk.Checkbutton(
            self.preview_settings_frame,
            text="Do formatting",
            bg="white",
            activebackground="white",
            variable=self.do_formatting_var,
            command=self.update_preview,
        )
        self.do_formatting_checkbox.grid(row=0, column=0, padx=5)

        #       Text preview text code toggle
        self.do_text_codes_var = tk.BooleanVar(value=True)
        self.prev_do_text_codes = tk.BooleanVar(value=self.do_text_codes_var.get())
        self.do_text_codes_checkbox = tk.Checkbutton(
            self.preview_settings_frame,
            text="Do text codes",
            bg="white",
            activebackground="white",
            variable=self.do_text_codes_var,
            command=self.update_preview,
        )
        self.do_text_codes_checkbox.grid(row=0, column=1, padx=5)

        #       Text preview .txt saving
        self.save_text_button = tk.Button(
            self.preview_settings_frame,
            text="Save text",
            command=self.save_text,
        )
        self.save_text_button.grid(row=0, column=2, padx=5)

        self.preview_window.bind("<Control-Key-1>", lambda _event: self.toggle_formatting())
        self.preview_window.bind("<Control-Key-2>", lambda _event: self.toggle_text_codes())
        self.preview_window.bind("<Control-Key-3>", lambda _event: self.save_text())

        #   Text preview
        tk.Label(self.preview_window, text="Text preview", font=("Arial", 12, "bold"), bg="white").pack(padx=5, pady=5)
        self.preview_text_area = setup_text_popup_window(self.preview_window, undo=True)
        self.bind_text_box_stuff(self.preview_text_area)

        self.preview_window.update_idletasks()
        self.preview_window.focus_force()

        self.text_text_area.focus_force()

        self.window_list: list[tk.Tk | tk.Toplevel] = [
            self.root,
            self.tags_window,
            self.codes_window,
            self.preview_window,
        ]

        for idx, window in enumerate(self.window_list):
            window.bind("<Control-Prior>", lambda _event: self.cycle_windows(-1))
            window.bind("<Control-Next>", lambda _event: self.cycle_windows(1))

            window.bind("<Control-q>", lambda _event: self.bring_all_windows_up())
            window.bind("<Control-Q>", lambda _event: self.bring_all_windows_up())
            window.bind("<FocusIn>", lambda event, window_idx=idx: self.check_window_focus(event, window_idx))

            window.bind("<Control-o>", lambda _event: self.load_text())
            window.bind("<Control-O>", lambda _event: self.load_text())
            window.bind("<Control-s>", lambda _event: self.save_text())
            window.bind("<Control-S>", lambda _event: self.save_text())
            window.bind("<Control-Shift-s>", lambda _event: self.save_text(save_as=True))
            window.bind("<Control-Shift-S>", lambda _event: self.save_text(save_as=True))

        self.current_important_view = 0
        self.important_views: list[tk.Toplevel | tk.Text] = [
            self.text_text_area,
            self.tags_text_area,
            self.codes_text_area,
            self.preview_window,
        ]

    def load_text(self) -> None:
        if not self.saved_text_progress:
            response = messagebox.askyesno(
                "Saving progress",
                "You still have unsaved work, and loading a text will overwrite everything that's written\nAre you SURE you want to continue loading?",
            )

            if not response:
                messagebox.showinfo(
                    "Loading status",
                    "Loading has been canceled and your unsaved work is available to edit",
                )
                return

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_path:
            messagebox.showwarning(
                "File loading",
                "To load a text, you have to provide a valid file path!",
            )
            return

        content_lines = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content_lines = [line.strip() for line in f.readlines()]
        except Exception as e:
            messagebox.showerror("File loading", f"An error was encountered while loading\nError: {e}")
            return

        full_filename = os.path.basename(file_path)

        try:
            text_content_idx = content_lines.index(f"TEXT_CONTENT_OF_{full_filename}:")
            tag_content_idx = content_lines.index(f"TAG_CONTENT_OF_{full_filename}:")
            code_content_idx = content_lines.index(f"CODE_CONTENT_OF_{full_filename}:")

        except ValueError as e:
            messagebox.showerror(
                "File loading",
                "This is an invalid save file!\nSave files cannot be edited in any way" "\nexcept for saving in the program",
            )

            self.reset_prev_text()

            return
        except Exception as e:
            messagebox.showerror(
                "File loading",
                f"An unknown error has occurred.\nIf you are not the maintainer of this project, let them know about this bug\nError: {e}",
            )

            return

        loaded_text_content = "\n".join(content_lines[text_content_idx + 2 : tag_content_idx - 3])
        loaded_tag_content = "\n".join(content_lines[tag_content_idx + 2 : code_content_idx - 3])
        loaded_code_content = "\n".join(content_lines[code_content_idx + 2 : -1])

        all_loaded_content = [loaded_text_content, loaded_tag_content, loaded_code_content]
        text_areas = [self.text_text_area, self.tags_text_area, self.codes_text_area]

        for text_area, loaded_content in zip(text_areas, all_loaded_content):
            clear_text_area(text_area)
            text_area_state = text_area.cget("state")
            text_area.config(state="normal")

            text_area.insert(tk.END, loaded_content)

            text_area.config(state=text_area_state)

        self.update_preview()
        self.saved_text_progress = True
        self.text_file_path = file_path

        for window in self.window_list:
            if window.title().endswith("*"):
                window.title(window.title()[:-1])

        self.preview_text_area.yview("1.0")

        messagebox.showinfo("File loading", "File loaded successfully!")

    def save_txt_file(self, file_path: str, content: str, show_success: bool = True) -> bool:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            if show_success:
                messagebox.showinfo("File saving", "File saved successfully!")

            return True
        except Exception as e:
            messagebox.showerror("File saving", f"An error was encountered while saving\nError: {e}")

            return False

    def _add_suffix_to_file_name(self, file_path: str, suffix: str) -> str:
        directory_to_file = os.path.dirname(file_path)
        full_file_name = os.path.basename(file_path)
        file_name_minus_extension = ".".join(full_file_name.split(".")[:-1])
        return os.path.join(directory_to_file, file_name_minus_extension + suffix + ".txt")

    def save_text(self, save_as: bool = False) -> None:
        last_important_view_idx = self.current_important_view

        if self.text_file_path is None or save_as:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            )

            if not file_path:
                messagebox.showwarning(
                    "File saving",
                    "To save the text, you have to provide a valid file path!",
                )
                return
        else:
            file_path = self.text_file_path

        full_filename = os.path.basename(file_path)
        full_txt_content = [
            f"TEXT_CONTENT_OF_{full_filename}:",
            '"""',
            self.text_text_area.get("1.0", "end-1c"),
            '"""',
            "\n",
            f"TAG_CONTENT_OF_{full_filename}:",
            '"""',
            self.tags_text_area.get("1.0", "end-1c"),
            '"""',
            "\n",
            f"CODE_CONTENT_OF_{full_filename}:",
            '"""',
            self.codes_text_area.get("1.0", "end-1c"),
            '"""',
        ]
        if not self.save_txt_file(file_path, "\n".join(full_txt_content)):
            return

        self.update_preview()

        self.saved_text_progress = True
        self.text_file_path = file_path

        for window in self.window_list:
            if window.title().endswith("*"):
                window.title(window.title()[:-1])

        self.focus_on_window_with_idx(last_important_view_idx)

    def read_tags(self, force_read: bool = False) -> dict[str, dict[str, Any]]:  # TODO
        if not self.do_formatting_var.get() and not force_read:
            return {}

        """
        make separate functions for reading tuple, strings, ints, floats, and dicts

        full list:
        string, ints, floats, booleans, tuples

        make everything into 1 line and remove all the spaces
        find all the key value pairs in the main dict, then parse each dict individually

        make it so that something only becomes a string if explicitely defined (with "" marks), or when 
           it's made up of letters (a through z, either lower or uppercase)
        numbers are by default made into ints/floats
        bools are by default made into bools
        """

        return {
            "TRUE_SUBSCRIPT": {
                "font": ("Arial", 8),
                "offset": -3,
            },
            "BOLD": {
                "font": ("Arial", 11, "bold"),
            },
            "H1": {
                "font": ("Arial", 15, "bold"),
            },
            "H2": {
                "font": ("Arial", 13, "bold"),
            },
        }

    def read_codes(self, force_read: bool = False) -> dict[str, str]:  # TODO
        if not self.do_text_codes_var.get() and not force_read:
            return {}

        """
        write code that can read lines like variable names:
        HI = "hi"
        TAB = "   "
        etc.

        
        allow for backslash continuations:
        REALLY_LONG = "yeah, this it"\
        "pretty long, but it doesn't"\
        "contain any new lines"

        
        idea for reading:
        read through the lines one by one

        reading:
        if a line is empty, skip
        if a line isn't empty, doesn't have an equal sign, and isn't after a line with a backslash, error
        if a line has an equal sign, then read it, if there's a backslash, check the next line
        if the next line doesn't have a string, error
        else, read it and check if it has a backslash
        repeat from reading:

        
        if the function errors, just return the same codes from before the change
        """

        return {
            "TAB": "    ",
            "TRUE_COORD_I": "(x[TRUE_SUBSCRIPT]i[TRUE_SUBSCRIPT/], y[TRUE_SUBSCRIPT]i[TRUE_SUBSCRIPT/])",
        }

    def copy_txt_to_clipboard(self, text: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def updated_text_area(self, idx: int, update_preview: bool = True) -> None:
        prev_text_content_list = [
            self.prev_text_text_content,
            self.prev_tags_text_content,
            self.prev_codes_text_content,
        ]

        text_area_list = [
            self.text_text_area,
            self.tags_text_area,
            self.codes_text_area,
        ]

        if prev_text_content_list[idx].get() == self.get_text_area_content(text_area_list[idx]):
            return

        self.add_asterisk_to_window_idx(idx)
        self.saved_text_progress = False

        if update_preview:
            self.root.after_idle(self.update_preview)
        else:
            prev_text_content_list[idx].set(self.get_text_area_content(text_area_list[idx]))

    def add_asterisk_to_window_idx(self, idx: int) -> None:
        if not self.window_list[idx].title().endswith("*"):
            self.window_list[idx].title(self.window_list[idx].title() + "*")

    def update_preview(self) -> None:
        if (
            self.prev_text_text_content.get() == self.get_text_area_content(self.text_text_area)
            and self.prev_tags_text_content.get() == self.get_text_area_content(self.tags_text_area)
            and self.prev_codes_text_content.get() == self.get_text_area_content(self.codes_text_area)
            and self.prev_do_formatting.get() == self.do_formatting_var.get()
            and self.prev_do_text_codes.get() == self.do_text_codes_var.get()
        ):
            return

        self.reset_prev_text()
        self.prev_do_formatting.set(self.do_formatting_var.get())
        self.prev_do_text_codes.set(self.do_text_codes_var.get())

        prev_preview_text_area = self.get_text_area_content(self.preview_text_area)

        clear_text_area(self.preview_text_area)
        errors, warnings, formatted_text = tkinter_text_tag_formatter(
            text_area=self.preview_text_area,
            tagged_and_coded_text=self.get_text_area_content(self.text_text_area),
            formatting_tags=self.read_tags(),
            text_codes=self.read_codes(),
            do_formatting=self.do_formatting_var.get(),
            replace_text_codes=self.do_text_codes_var.get(),
            show_errors_in_window=False,
            crash_on_error=False,
            show_warnings_in_window=False,
            return_errors=True,
            return_warnings=True,
            return_formatted_text=True,
        )

        self.scroll_to_text_diff(
            self.preview_text_area,
            self.get_text_diff_plus_buffer(
                prev_preview_text_area,
                formatted_text,
                num_char_buffer=50,
            ),
        )

        self.preview_text_area.config(bg="white")

        if len(warnings) > 1:
            self.preview_text_area.config(bg="gold")

        if len(errors) > 0:
            self.preview_text_area.config(bg="firebrick1")

    def find_text_diff_idx(self, prev_text: str, new_text: str) -> int:
        if prev_text == new_text:
            return -1

        for i, (char1, char2) in enumerate(zip(prev_text, new_text)):
            if char1 != char2:
                return i

        if new_text.startswith(prev_text) or prev_text.startswith(new_text):
            return len(new_text) - 1

        return -1

    def get_text_diff_plus_buffer(self, prev_text: str, new_text: str, num_char_buffer: int = 25) -> str:
        if num_char_buffer < 0:
            raise ValueError("num_char_buffer CANNOT be less than 0")

        idx = self.find_text_diff_idx(prev_text, new_text)

        if idx == -1:
            return ""

        return new_text[idx - num_char_buffer : idx + 1 + num_char_buffer]

    def scroll_to_text_diff(self, text_area: tk.Text, changed_text: str) -> None:
        if not changed_text:
            return

        text_area.update_idletasks()

        match_idx = text_area.search(changed_text, "1.0", stopindex=tk.END, exact=True)

        text_area.yview(match_idx)
        
        text_area.update_idletasks() 
        
        line_data = text_area.dlineinfo(match_idx)
        
        # if line_data:
        #     line_height = line_data[3]
        #     widget_height = text_area.winfo_height()
            
        #     visible_units = widget_height // line_height
            
        #     text_area.yview_scroll(-(visible_units // 2), "units")

    def clear_and_update(self, text_area: tk.Text) -> None:
        clear_text_area(text_area)
        self.update_preview()

    def reset_prev_text(self) -> None:
        self.prev_text_text_content.set(self.get_text_area_content(self.text_text_area))
        self.prev_tags_text_content.set(self.get_text_area_content(self.tags_text_area))
        self.prev_codes_text_content.set(self.get_text_area_content(self.codes_text_area))

    def toggle_formatting(self) -> None:
        self.do_formatting_var.set(not self.do_formatting_var.get())
        self.update_preview()

    def toggle_text_codes(self) -> None:
        self.do_text_codes_var.set(not self.do_text_codes_var.get())
        self.update_preview()

    def focus_on_window_with_idx(self, idx: int) -> None:
        self.window_list[idx].deiconify()
        self.window_list[idx].lift()
        self.important_views[idx].focus_force()

    def cycle_windows(self, dir: Literal[-1, 1]) -> None:
        self.current_important_view = (self.current_important_view + dir) % len(self.important_views)
        self.focus_on_window_with_idx(self.current_important_view)

    def bring_all_windows_up(self) -> None:
        for _ in range(4):
            self.cycle_windows(1)

    def check_window_focus(self, event: tk.Event, window_idx: int) -> None:
        if event.widget == self.window_list[window_idx]:
            self.current_important_view = window_idx

    # AI generated
    def text_box_undo(self, event: tk.Event) -> str:
        try:
            event.widget.edit_undo()
        except tk.TclError:
            pass
        return "break"

    # AI generated
    def text_box_redo(self, event: tk.Event) -> str:
        try:
            event.widget.edit_redo()
        except tk.TclError:
            pass
        return "break"

    # AI generated
    def text_box_ctrl_backspace(self, event: tk.Event) -> str:
        widget = event.widget
        text_before = widget.get("insert linestart", "insert")

        if not text_before:
            if widget.index("insert") != "1.0":
                widget.delete("insert - 1 chars", "insert")
            return "break"

        # Regex Breakdown:
        # \w+ matches the word
        # \s? matches an optional single space directly on the left of the cursor
        # $ anchors it to the cursor's exact position
        match = re.search(r"\w+\s?$", text_before)
        if not match:
            # Fallback: if it's punctuation or multiple spaces, just grab the non-word characters
            match = re.search(r"\W+\s?$", text_before)

        if match:
            num_chars = len(match.group(0))
            widget.delete(f"insert - {num_chars} chars", "insert")

        return "break"

    # AI generated
    def text_box_ctrl_delete(self, event: tk.Event) -> str:
        widget = event.widget
        text_after = widget.get("insert", "insert lineend")

        if not text_after:
            if widget.index("insert lineend") != widget.index("end - 1 chars"):
                widget.delete("insert", "insert + 1 chars")
            return "break"

        # Case 1: Cursor is directly to the left of space(s)
        # Delete all spaces, stop at the next word/character
        match = re.match(r"^\s+", text_after)

        if not match:
            # Case 2: Cursor is directly to the left of a word
            # Delete the word AND all consecutive spaces to its right
            match = re.match(r"^\w+\s*", text_after)

        if not match:
            # Fallback: Cursor is directly to the left of punctuation
            # Delete consecutive punctuation marks
            match = re.match(r"^[^\w\s]+", text_after)

        if match:
            num_chars = len(match.group(0))
            widget.delete("insert", f"insert + {num_chars} chars")

        return "break"

    # AI generated
    def text_box_ctrl_left_arrow(self, event: tk.Event) -> str:
        widget = event.widget
        text_before = widget.get("insert linestart", "insert")

        if widget.tag_ranges("sel"):
            widget.tag_remove("sel", "1.0", "end")

        if not text_before:
            # If at the start of a line, jump to the end of the previous line
            if widget.index("insert") != "1.0":
                widget.mark_set("insert", "insert - 1 line lineend")
                widget.see("insert")  # Ensure the cursor stays visible
            return "break"

        # Match a word (\w+) OR punctuation ([^\w\s]+), followed by any number of optional spaces (\s*)
        # $ anchors the search to the exact position of the cursor
        match = re.search(r"(\w+|[^\w\s]+)\s*$", text_before)

        if not match:
            # Fallback: If there are multiple spaces before the cursor, jump past them
            match = re.search(r"\s+$", text_before)

        if match:
            num_chars = len(match.group(0))
            widget.mark_set("insert", f"insert - {num_chars} chars")
            widget.see("insert")

        return "break"

    # AI generated
    def text_box_ctrl_right_arrow(self, event: tk.Event) -> str:
        widget = event.widget
        text_after = widget.get("insert", "insert lineend")

        if widget.tag_ranges("sel"):
            widget.tag_remove("sel", "1.0", "end")

        if not text_after:
            # If at the end of a line, jump to the start of the next line
            if widget.index("insert lineend") != widget.index("end - 1 chars"):
                widget.mark_set("insert", "insert + 1 line linestart")
                widget.see("insert")
            return "break"

        # Case 1: Cursor is directly to the left of a space. Match a single space.
        match = re.match(r"^\s", text_after)

        if not match:
            # Case 2: Cursor is to the left of a word or punctuation.
            # Match the word (\w+) OR punctuation ([^\w\s]+), plus any number of optional spaces (\s*)
            match = re.match(r"^(\w+|[^\w\s]+)\s*", text_after)

        if match:
            num_chars = len(match.group(0))
            widget.mark_set("insert", f"insert + {num_chars} chars")
            widget.see("insert")

        return "break"

    # AI generated
    def text_box_ctrl_shift_left_arrow(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")

        text_before = widget.get("insert linestart", "insert")

        if not text_before:
            if widget.index("insert") != "1.0":
                widget.mark_set("insert", "insert - 1 line lineend")
        else:
            match = re.search(r"(\w+|[^\w\s]+)\s*$", text_before)
            if not match:
                match = re.search(r"\s+$", text_before)

            if match:
                num_chars = len(match.group(0))
                widget.mark_set("insert", f"insert - {num_chars} chars")

        widget.tag_remove("sel", "1.0", "end")

        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_ctrl_shift_right_arrow(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")

        text_after = widget.get("insert", "insert lineend")

        if not text_after:
            if widget.index("insert lineend") != widget.index("end - 1 chars"):
                widget.mark_set("insert", "insert + 1 line linestart")
        else:
            match = re.match(r"^\s+", text_after)
            if not match:
                match = re.match(r"^(\w+|[^\w\s]+)\s*", text_after)

            if match:
                num_chars = len(match.group(0))
                widget.mark_set("insert", f"insert + {num_chars} chars")

        widget.tag_remove("sel", "1.0", "end")

        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_double_click(self, event: tk.Event) -> str:
        widget = event.widget

        click_index = widget.index(f"@{event.x},{event.y}")
        line, col = click_index.split(".")
        col = int(col)

        line_text = widget.get(f"{line}.0", f"{line}.end")

        if col >= len(line_text):
            return "break"

        # Regex breakdown for VS Code-like selection tokens:
        # \w+       -> matches alphanumeric words (letters, numbers, underscores)
        # [^\w\s]+  -> matches contiguous punctuation marks
        # \s+       -> matches contiguous spaces
        for match in re.finditer(r"\w+|[^\w\s]+|\s+", line_text):
            if match.start() <= col < match.end():
                widget.tag_remove("sel", "1.0", "end")

                start_index = f"{line}.{match.start()}"
                end_index = f"{line}.{match.end()}"

                widget.tag_add("sel", start_index, end_index)

                widget.mark_set("anchor", start_index)

                widget.mark_set("insert", end_index)
                break

        return "break"

    # AI generated
    def text_box_shift_left_click(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            current_index = widget.index("insert")
            widget.mark_set("anchor", current_index)

        click_index = widget.index(f"@{event.x},{event.y}")

        widget.tag_remove("sel", "1.0", "end")

        if widget.compare(click_index, "<", "anchor"):
            start_index = click_index
            end_index = "anchor"
        else:
            start_index = "anchor"
            end_index = click_index

        widget.tag_add("sel", start_index, end_index)

        widget.mark_set("insert", click_index)

        return "break"

    # AI generated
    def keep_cursor_solid(self, event: tk.Event) -> None:
        widget = event.widget

        # Immediately set the off-time to 0, making the cursor solid
        widget.configure(insertofftime=0)

        # If there's an existing countdown running from a previous keystroke, cancel it
        if widget._blink_timer is not None:
            widget.after_cancel(widget._blink_timer)

        widget._blink_timer = widget.after(500, lambda: widget.configure(insertofftime=widget._default_insertofftime))

    def bind_text_box_stuff(self, text_area: tk.Text) -> None:
        text_area.bind("<Control-z>", self.text_box_undo)
        text_area.bind("<Control-Z>", self.text_box_undo)

        text_area.bind("<Control-y>", self.text_box_redo)
        text_area.bind("<Control-Y>", self.text_box_redo)
        text_area.bind("<Control-Shift-z>", self.text_box_redo)
        text_area.bind("<Control-Shift-Z>", self.text_box_redo)

        text_area.bind("<Control-BackSpace>", self.text_box_ctrl_backspace)
        text_area.bind("<Control-Delete>", self.text_box_ctrl_delete)

        text_area.bind("<Control-Left>", self.text_box_ctrl_left_arrow)
        text_area.bind("<Control-Right>", self.text_box_ctrl_right_arrow)
        text_area.bind("<Control-Shift-Left>", self.text_box_ctrl_shift_left_arrow)
        text_area.bind("<Control-Shift-Right>", self.text_box_ctrl_shift_right_arrow)

        text_area.bind("<Double-Button-1>", self.text_box_double_click)

        text_area.bind("<Shift-Button-1>", self.text_box_shift_left_click)

        text_area._default_insertofftime = text_area.cget("insertofftime")
        text_area._blink_timer = None
        text_area.bind("<Key>", self.keep_cursor_solid)

    def get_text_area_content(self, text_area: tk.Text) -> str:
        return text_area.get("1.0", "end-1c")

    def open_help(self) -> None:
        if self.help_window != None:
            messagebox.showinfo(
                "Help guide",
                f"A window showing the help guide is already open",
            )
            self.help_window.deiconify()
            self.help_window.lift()
            self.help_window.focus_force()
            return

        self.help_window = create_popup_window_toplevel(
            self.root,
            f"Help guide",
            self.quit_help,
            full_quit_func=self.full_quit,
        )

        self.help_text_area = setup_text_popup_window(self.help_window)

        clear_text_area(self.help_text_area)
        tkinter_text_tag_formatter(
            self.help_text_area,
            HELP_GUIDE_FOR_TEXT_WRITER,
            TAGS_FOR_HELP_GUIDE,
            CODES_FOR_HELP_GUIDE,
        )

        set_max_window_size_with_text(self.help_window, self.help_text_area)

        self.help_window.focus_force()

    def quit_help(self, _event: tk.Event | None = None) -> None:
        self.help_window.destroy()
        self.help_text_area = None

    def run_gui(self) -> None:
        self.root.mainloop()

    def quit(self, _event=None) -> None:
        if not self.saved_text_progress:
            response = messagebox.askyesno("Unsaved work", "You still have unsaved work! Are you sure you want to quit now?")

            if not response:
                messagebox.showinfo(
                    "Unsaved work",
                    "The quit has been canceled, you can now save your progress",
                )
                return

        self.root.destroy()

    def full_quit(self, _event=None) -> None:
        if not self.saved_text_progress:
            response = messagebox.askyesno("Unsaved work", "You still have unsaved work! Are you sure you want to quit now?")

            if not response:
                messagebox.showinfo(
                    "Unsaved work",
                    "The quit has been canceled, you can now save your progress",
                )
                return

        self.root.destroy()


if __name__ == "__main__":
    formatted_text_writer = FormattedTextWriter()
    formatted_text_writer.run_gui()
