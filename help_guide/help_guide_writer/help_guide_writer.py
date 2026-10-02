import os
import re
import tkinter as tk
from typing import Literal, Any
from tkinter import filedialog, messagebox
from interactive_displays.text_popup_window import (
    setup_text_popup_window,
    create_popup_window_toplevel,
)
from tkinter_text_renderer.tkinter_text_renderer import (
    TEXT_CODE,
    OPENING_TAG,
    CLOSING_TAG,
    clear_text_area,
    tkinter_text_tag_formatter,
)

HELP_GUIDE_FOR_HELP_GUIDE_WRITER = """"""
TAGS_FOR_HELP_GUIDE_WRITER = {}
CODES_FOR_HELP_GUIDE_WRITER = {}


class HelpGuideWriter:
    def __init__(self, title="Help guide writer", offset_x: float = 40, offset_y: float = 40):
        self.root = tk.Tk()
        self.root.title(title)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight() - 2 * offset_y
        self.root.geometry(
            f"{(self.screen_width - offset_x)//3 - offset_x}x{self.screen_height - 2*offset_y}+{offset_x}+{offset_y}"
        )

        self.root.bind("<Control-w>", self.quit)
        self.root.bind("<Control-W>", self.full_quit)
        self.root.bind("<Escape>", self.quit)

        self.saved_guide_progress = True

        # Setting up the main writing area
        self.root.config(bg="white")
        tk.Label(self.root, text="Write guide here", font=("Arial", 12, "bold"), bg="white").pack(padx=5, pady=5)
        self.guide_options_frame = tk.Frame(self.root, bg="white")
        self.guide_options_frame.pack(fill=tk.X, padx=5, pady=5)
        self.guide_options_frame.columnconfigure(0, weight=1)
        self.guide_options_frame.columnconfigure(1, weight=1)
        self.guide_options_frame.columnconfigure(2, weight=1)

        self.load_guide_button = tk.Button(
            self.guide_options_frame,
            text="Load guide",
            command=self.load_guide,
        )
        self.load_guide_button.grid(row=0, column=0, padx=5, pady=5)

        self.open_help_for_help_guide_writer_button = tk.Button(
            self.guide_options_frame,
            text="Help",
            command=self.open_help,
        )
        self.open_help_for_help_guide_writer_button.grid(row=0, column=1, padx=5, pady=5)
        self.help_window = None

        self.clear_guide_button = tk.Button(
            self.guide_options_frame,
            text="Clear guide",
        )
        self.clear_guide_button.grid(row=0, column=2, padx=5, pady=5)

        self.guide_text_area = setup_text_popup_window(self.root, undo=True)
        self.prev_guide_text_content = self.get_text_area_content(self.guide_text_area)
        self.clear_guide_button.config(command=lambda: self.clear_and_update(self.guide_text_area))
        self.bind_text_box_stuff(self.guide_text_area)
        self.guide_text_area.config(state="normal")
        self.guide_text_area.bind("<KeyRelease>", lambda _event: self.root.after_idle(self.update_preview))

        self.root.bind("<Control-Key-1>", lambda _event: self.load_guide())
        self.root.bind("<Control-Key-2>", lambda _event: self.clear_and_update(self.guide_text_area))

        # Setting up root values
        self.root.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Setting up where the formatting tags are defined
        self.tags_window = create_popup_window_toplevel(
            self.root,
            "Help guide formatting",
            self.quit,
            custom_geometry=f"{root_width}x{(self.screen_height - offset_y)//2 - offset_y}+{root_x + root_width + offset_x}+{root_y}",
            full_quit_func=self.full_quit,
        )
        self.tags_window.config(bg="white")
        tk.Label(
            self.tags_window,
            text="Formatting tags (Write like dict, minus the outer curly braces)",
            font=("Arial", 12, "bold"),
            bg="white",
        ).pack(padx=5, pady=5)
        self.clear_tags_button = tk.Button(
            self.tags_window,
            text="Clear tags",
        )
        self.clear_tags_button.pack(padx=5, pady=5)
        self.tags_text_area = setup_text_popup_window(self.tags_window, undo=True)
        self.prev_tags_text_content = self.get_text_area_content(self.tags_text_area)
        self.clear_tags_button.config(command=lambda: self.clear_and_update(self.tags_text_area))
        self.bind_text_box_stuff(self.tags_text_area)
        self.tags_text_area.config(state="normal")
        self.tags_text_area.bind("<KeyRelease>", lambda _event: self.root.after_idle(self.update_preview))

        self.tags_window.bind("<Control-Key-1>", lambda _event: self.clear_and_update(self.tags_text_area))

        self.tags_window.update_idletasks()
        self.tags_window.focus_force()

        # Setting up where the text codes are defined
        self.codes_window = create_popup_window_toplevel(
            self.root,
            "Help guide formatting",
            self.quit,
            custom_geometry=f"{root_width}x{(self.screen_height - offset_y)//2 - offset_y}+{root_x + root_width + offset_x}+{root_y + (self.screen_height - offset_y)//2}",
            full_quit_func=self.full_quit,
        )
        self.codes_window.config(bg="white")
        tk.Label(
            self.codes_window,
            text="Text codes (Write like dict, minus the outer curly braces)",
            font=("Arial", 12, "bold"),
            bg="white",
        ).pack(padx=5, pady=5)
        self.clear_codes_button = tk.Button(
            self.codes_window,
            text="Clear tags",
        )
        self.clear_codes_button.pack(padx=5, pady=5)
        self.codes_text_area = setup_text_popup_window(self.codes_window, undo=True)
        self.prev_codes_text_content = self.get_text_area_content(self.codes_text_area)
        self.clear_codes_button.config(command=lambda: self.clear_and_update(self.codes_text_area))
        self.bind_text_box_stuff(self.codes_text_area)
        self.codes_text_area.config(state="normal")
        self.codes_text_area.bind("<KeyRelease>", lambda _event: self.root.after_idle(self.update_preview))

        self.codes_window.bind("<Control-Key-1>", lambda _event: self.clear_and_update(self.codes_text_area))

        self.codes_window.update_idletasks()
        self.codes_window.focus_force()

        # Setting up where the preview is
        self.preview_window = create_popup_window_toplevel(
            self.root,
            "Help guide preview",
            self.quit,
            custom_geometry=f"{root_width}x{root_height}+{root_x + 2*root_width + 2*offset_x}+{root_y}",
            full_quit_func=self.full_quit,
        )
        self.preview_window.config(bg="white")

        #   Guide preview settings
        tk.Label(self.preview_window, text="Guide preview settings", font=("Arial", 12, "bold"), bg="white").pack(
            padx=5, pady=5
        )
        self.preview_settings_frame = tk.Frame(self.preview_window, bg="white")
        self.preview_settings_frame.pack(fill=tk.X, pady=5)
        self.preview_settings_frame.columnconfigure(0, weight=1)
        self.preview_settings_frame.columnconfigure(1, weight=1)
        self.preview_settings_frame.columnconfigure(2, weight=1)

        #       Guide preview formatting toggle
        self.do_formatting_var = tk.BooleanVar(value=True)
        self.prev_do_formatting = self.do_formatting_var.get()
        self.do_formatting_checkbox = tk.Checkbutton(
            self.preview_settings_frame,
            text="Do formatting",
            bg="white",
            activebackground="white",
            variable=self.do_formatting_var,
            command=self.update_preview,
        )
        self.do_formatting_checkbox.grid(row=0, column=0, padx=5)

        #       Guide preview text code toggle
        self.do_text_codes_var = tk.BooleanVar(value=True)
        self.prev_do_text_codes = self.do_text_codes_var.get()
        self.do_text_codes_checkbox = tk.Checkbutton(
            self.preview_settings_frame,
            text="Do text codes",
            bg="white",
            activebackground="white",
            variable=self.do_text_codes_var,
            command=self.update_preview,
        )
        self.do_text_codes_checkbox.grid(row=0, column=1, padx=5)

        #       Guide preview .txt saving
        self.save_guide_button = tk.Button(
            self.preview_settings_frame,
            text="Save guide",
            command=self.save_guide,
        )
        self.save_guide_button.grid(row=0, column=2, padx=5)

        self.preview_window.bind("<Control-Key-1>", lambda _event: self.toggle_formatting())
        self.preview_window.bind("<Control-Key-2>", lambda _event: self.toggle_text_codes())
        self.preview_window.bind("<Control-Key-3>", lambda _event: self.save_guide())

        #   Guide preview
        tk.Label(self.preview_window, text="Guide preview", font=("Arial", 12, "bold"), bg="white").pack(padx=5, pady=5)
        self.preview_text_area = setup_text_popup_window(self.preview_window, undo=True)
        self.bind_text_box_stuff(self.preview_text_area)

        self.preview_window.update_idletasks()
        self.preview_window.focus_force()

        self.guide_text_area.focus_force()

        self.window_list: list[tk.Tk | tk.Toplevel] = [
            self.root,
            self.tags_window,
            self.codes_window,
            self.preview_window,
        ]

        for window in self.window_list:
            window.bind("<Control-Prior>", lambda _event: self.cycle_guides(-1))
            window.bind("<Control-Next>", lambda _event: self.cycle_guides(1))

        self.current_important_view = 0
        self.important_views: list[tk.Toplevel | tk.Text] = [
            self.guide_text_area,
            self.tags_text_area,
            self.codes_text_area,
            self.preview_window,
        ]

    def load_guide(self) -> None:
        if not self.saved_guide_progress:
            response = messagebox.askyesno(
                "Saving progress",
                "You still have unsaved work, and loading a guide will overwrite everything that's written\nAre you SURE you want to continue loading?",
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
                "To load a guide, you have to provide a valid file path!",
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
        guide_content_idx = content_lines.index(f"GUIDE_CONTENT_OF_{full_filename}:")
        tag_content_idx = content_lines.index(f"TAG_CONTENT_OF_{full_filename}:")
        code_content_idx = content_lines.index(f"CODE_CONTENT_OF_{full_filename}:")

        loaded_guide_content = "\n".join(content_lines[guide_content_idx + 1 : tag_content_idx - 2])
        loaded_tag_content = "\n".join(content_lines[tag_content_idx + 1 : code_content_idx - 2])
        loaded_code_content = "\n".join(content_lines[code_content_idx + 1 :])

        all_loaded_content = [loaded_guide_content, loaded_tag_content, loaded_code_content]
        text_areas = [self.guide_text_area, self.tags_text_area, self.codes_text_area]

        for text_area, loaded_content in zip(text_areas, all_loaded_content):
            clear_text_area(text_area)
            text_area_state = text_area.cget("state")
            text_area.config(state="normal")

            text_area.insert(tk.END, loaded_content)

            text_area.config(state=text_area_state)

        self.update_preview()
        self.saved_guide_progress = True

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

    def save_guide(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_path:
            messagebox.showwarning(
                "File saving",
                "To save the guide, you have to provide a valid file path!",
            )
            return

        full_filename = os.path.basename(file_path)
        full_txt_content = [
            f"GUIDE_CONTENT_OF_{full_filename}:",
            self.guide_text_area.get("1.0", "end-1c"),
            "\n",
            f"TAG_CONTENT_OF_{full_filename}:",
            self.tags_text_area.get("1.0", "end-1c"),
            "\n",
            f"CODE_CONTENT_OF_{full_filename}:",
            self.codes_text_area.get("1.0", "end-1c"),
        ]
        if not self.save_txt_file(file_path, "\n".join(full_txt_content)):
            return

        self.saved_guide_progress = True

    def read_tags(self) -> dict[str, dict[str, Any]]:  # TODO
        if not self.do_formatting_var.get():
            return {}

        return {
            "SUBSCRIPT": {
                "font": ("Arial", 8),
                "offset": -3,
            },
            "BOLD": {
                "font": ("Arial", 11, "bold"),
            },
        }

    def read_codes(self) -> dict[str, str]:  # TODO
        if not self.do_text_codes_var.get():
            return {}

        return {"TAB": "    "}

    def update_preview(self) -> None:
        if (
            self.prev_guide_text_content == self.get_text_area_content(self.guide_text_area)
            and self.prev_tags_text_content == self.get_text_area_content(self.tags_text_area)
            and self.prev_codes_text_content == self.get_text_area_content(self.codes_text_area)
            and self.prev_do_formatting == self.do_formatting_var.get()
            and self.prev_do_text_codes == self.do_text_codes_var.get()
        ):
            return

        self.prev_guide_text_content = self.get_text_area_content(self.guide_text_area)
        self.prev_tags_text_content = self.get_text_area_content(self.tags_text_area)
        self.prev_codes_text_content = self.get_text_area_content(self.codes_text_area)
        self.prev_do_formatting = self.do_formatting_var.get()
        self.prev_do_text_codes = self.do_text_codes_var.get()

        self.saved_guide_progress = False

        clear_text_area(self.preview_text_area)
        errors, warnings = tkinter_text_tag_formatter(
            self.preview_text_area,
            self.get_text_area_content(self.guide_text_area),
            self.read_tags(),
            self.read_codes(),
            self.do_formatting_var.get(),
            self.do_text_codes_var.get(),
            False,
            False,
            False,
            True,
            True,
        )
        
        self.preview_text_area.config(bg="white")
        
        if len(warnings) > 1:
            self.preview_text_area.config(bg="gold")
        
        if len(errors) > 0:
            self.preview_text_area.config(bg="firebrick1")

    def clear_and_update(self, text_area: tk.Text) -> None:
        clear_text_area(text_area)
        self.update_preview()

    def toggle_formatting(self) -> None:
        self.do_formatting_var.set(not self.do_formatting_var.get())
        self.update_preview()

    def toggle_text_codes(self) -> None:
        self.do_text_codes_var.set(not self.do_text_codes_var.get())
        self.update_preview()

    def cycle_guides(self, dir: Literal[-1, 1]) -> None:
        self.current_important_view = (self.current_important_view + dir) % len(self.important_views)
        self.important_views[self.current_important_view].focus_force()

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

    def bind_text_box_stuff(self, text_area: tk.Text) -> None:
        text_area.bind("<Control-z>", self.text_box_undo)
        text_area.bind("<Control-Z>", self.text_box_undo)

        text_area.bind("<Control-y>", self.text_box_redo)
        text_area.bind("<Control-Y>", self.text_box_redo)
        text_area.bind("<Control-Shift-z>", self.text_box_redo)
        text_area.bind("<Control-Shift-Z>", self.text_box_redo)

        text_area.bind("<Control-BackSpace>", self.text_box_ctrl_backspace)
        text_area.bind("<Control-Delete>", self.text_box_ctrl_delete)

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
            HELP_GUIDE_FOR_HELP_GUIDE_WRITER,
            TAGS_FOR_HELP_GUIDE_WRITER,
            CODES_FOR_HELP_GUIDE_WRITER,
        )

        self.help_window.focus_force()

    def quit_help(self, _event: tk.Event | None = None) -> None:
        self.help_window.destroy()
        self.help_text_area = None

    def run_gui(self) -> None:
        self.root.mainloop()

    def quit(self, _event=None) -> None:
        if not self.saved_guide_progress:
            response = messagebox.askyesno("Unsaved work", "You still have unsaved work! Are you sure you want to quit now?")

            if not response:
                messagebox.showinfo(
                    "Unsaved work",
                    "The quit has been canceled, you can now save your progress",
                )
                return

        self.root.destroy()

    def full_quit(self, _event=None) -> None:
        if not self.saved_guide_progress:
            response = messagebox.askyesno("Unsaved work", "You still have unsaved work! Are you sure you want to quit now?")

            if not response:
                messagebox.showinfo(
                    "Unsaved work",
                    "The quit has been canceled, you can now save your progress",
                )
                return

        self.root.destroy()


if __name__ == "__main__":
    help_guide_writer = HelpGuideWriter()
    help_guide_writer.run_gui()
