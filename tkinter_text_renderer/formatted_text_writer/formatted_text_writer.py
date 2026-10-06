import os
import re
import tkinter as tk
from typing import Literal, Any
from tkinter import filedialog, messagebox
from tkinter_text_renderer.formatted_text_writer.str_to_type_parser import parse_fundamental_or_dict_or_tuple
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
    append_to_text_area,
    find_all_occurrences,
    tkinter_text_tag_formatter,
)

# AI generated code is labeled with the comment "AI generated" before it
# If it was only partially AI generated, the comment will be "Partially AI generated"

HELP_GUIDE_FOR_TEXT_WRITER = f"""[/TAB][H1]Main text writing area:[H1/]\nIt has the title "Formatted text writer" and this is where all formatted text is written, including this text right here!\n\nYou can write text codes and text formatting tags here along with the text you want to show and edit.\n\nFormatting tags have an opening and closing tag to signify what text they\'re tagging.\nThe opening tags are written in the form {OPENING_TAG.format("TAG_NAME_HERE")}, and the closing tags are written in the form {CLOSING_TAG.format("TAG_NAME_HERE")}.\nSo for a "BOLD" tag, the opening and closing tags would be written like {OPENING_TAG.format("BOLD")} and {CLOSING_TAG.format("BOLD")}, with the text you want bolded in between the opening and closing tags.\n\nText codes are written in the form {TEXT_CODE.format("CODE_NAME_HERE")}, so for a "TAB" code, it would be written like {TEXT_CODE.format("TAB")}.\n\nIf there\'s an error in your formatting, then the preview window will turn red, and if there\'s a warning in your formatting, the preview window will turn yellow. When there\'s an error, formatting will stop completely, but if there\'s a warning, it\'ll still format everything.\nErrors happen when there\'s an open tag without a closing, or vice versa. And this usually happens with a typo or a missing "/" in the closing tag.\nWarnings happen when there\'s a closing tag between an opening and closing tag that doesn\'t correspond to either. For example, if there was an opening tag for red text, an opening tag for underlined text, a closing tag for red text, and then a closing tag for underlined text, there\'d be an error.\nWarning: [RED][UNDERLINED][RED/][UNDERLINED/]\nCorrect: [RED][UNDERLINED][UNDERLINED/][RED/]\n\nThere are 5 buttons at the top of the window which say "Load text", "New text", "Help", "Clear text", and "Copy text".\n1. Pressing the "Load text" button opens a popup to ask which .txt file you want to load in. It needs to be a valid .txt file from this program, otherwise it won\'t load correctly. The only way to guarantee that the .txt works is by saving the text you made and then later loading it in.\n2. Pressing the "New text" button clears all the text inputs and removes the link of the current edited text to any .txt file path.\n3. Pressing the "Help" button opens a window to explain how to use the entire program. That help guide was written in this very program!\n4. Pressing the "Clear text" button clears the text in this window. This action is able to be undone using Ctrl + Z.\n5. Pressing the "Copy text" button turns it into a valid Python string, which you can then paste into a triple quoted string. Do note that the copied text doesn\'t include the quotes, but only the text that goes inside the quotes.\n\n\n[/TAB][H1]Formatting tag area:[H1/]\n[H2]Basics[H2/]\nIt has the title "Formatted text formatting" and this is where all the formatting tags are defined.\n""" + """\nThese should be written like writing variables in Python. It should be in this form:\nTAG_NAME = { SETTING_NAME: VALUE_TO_SET }\n\nWhere "TAG_NAME" is the name you want for that code (rules on naming later), and "{ SETTING_NAME: VALUE_TO_SET }" to be the setting for the text property.\n\nFormatting tags are useful because they let you customize almost any property of text. You can change the font family, size, of styling (bold, italic, etc.), vertical positioning, color, background, etc.\n\nTo format text with a formatting tag, you need to use the opening and closing tag. So if you had a tag to turn text red named "RED", you\'d write the text like this:\nnon red text [RED]your red text here[RED/] non red text\n\nThere are 4 buttons at the top of the window which say "Clear tags", "Update preview", "Convert tags and copy", and "Copy tag text"\n1. Pressing "Clear tags" clears all the tags in the window, essentially allowing you to restart clean when writing tags.\n2. Pressing "Update preview" forces an update on the update window. This is because the tags window doesn\'t constantly update the preview with changes since you might not be finished with writing a tag.\n3. Pressing "Convert tags and copy" takes the tags you wrote, turns it into a dict and copies it to your clipboard. This lets you paste it into a Python file as is.\n4. Pressing "Copy tag text" takes all the text in the tag writing window and copies it to your clipboard. This lets you paste it as a string for testing or to place in any piece of code.\n\n[H2]Formatting tag rules[H2/]\nIt\'s not necessary, but it\'s recommended to make all the tags in all caps to make them distinct from normal text.\nMake sure there aren\'t any spaces in the tag name, this can lead to ambiguity in the tag name.\nAgain, these tags should be written like normal variables in Python.\n\nOnce you write the tag name, you can have any number of spaces, an equals sign, any number of spaces, and then a dictionary of values to change. Just like in Python, you can write all the parts of the dictionary in one line or split it into multiple lines. The keys of the dictionary should be the names of the tkinter Text attributes that can be edited through tags\nHere\'s a list to all the attributes that can be edited (NOT CLICKABLE):\n[HYPERLINK]https://www.tcl-lang.org/man/tcl8.5/TkCmd/text.htm#M26:~:text=non%2Delided%20index.-,TAGS,-The%20first%20form[HYPERLINK/]\n\nYou don\'t have to necessarily use quote marks to signify something is a string in the dictionary. If it\'s made up of numbers, it\'s assumed to be a float or integer (depending on whether or not there\'s a decimal point). If it\'s "True" or "False" (case insensitive), it\'ll assume it\'s a boolean. If it has parentheses, it\'s assumed to be a tuple. Otherwise, it\'s a string. You can explicitly make something a string by using quotes, double or single. If using strings, the definition of strings works the same as Python strings. Triple quotes, single quote in double quoted strings, double quote in single quoted strings, backslashes to split a string along different lines, and escape characters (\\\\, \\n, \\t, \\\', and \\") work. Though you can just type \\ instead of \\\\ as long as the next character isn\'t one belonging to the escape characters, because you might get accidental escape characters you didn\'t mean for.\n\n\n[/TAB][H1]Text code area:[H1/]\n[H2]Basics[H2/]\nIt has the title "Formatted text codes" and this is where all the text codes are defined.\n\nThese should be written like writing variables in Python. It should be in this form:\nCODE_NAME = "[TEXT_HERE]"\n\nWhere "CODE_NAME" is the name you want for that code (rules on naming later), and "[TEXT_HERE]" to be the text you want to the text codes\n\nThe reason why text codes are useful are that you can make a code that\'s later editable, like a TAB code, that you can later adjust how much spacing it adds, or it can be used to shorten extremely repetitive text. Like, if you wanted to write "(x[TRUE_SUBSCRIPT]i[TRUE_SUBSCRIPT/], y[TRUE_SUBSCRIPT]i[TRUE_SUBSCRIPT/])", you\'d have to constantly write:\n(x[SUBSCRIPT]i[SUBSCRIPT/], y[SUBSCRIPT]i[SUBSCRIPT/])\nWhich is extremely hard to read and repetitive, so you can write a text code like:\nCOORD_I = (x[SUBSCRIPT]i[SUBSCRIPT/], y[SUBSCRIPT]i[SUBSCRIPT/])\n\nSo instead of writing the mess of text from earlier, you could just write "[/COORD_I]" to get "[/TRUE_COORD_I]"\nThis makes writing formatted text much easier to read and navigate.\n\nThere are 4 buttons at the top of the window which say "Clear codes", "Update preview", "Convert codes and copy", and "Copy code text"\n1. Pressing "Clear codes" clears all the codes in the window, essentially allowing you to restart clean when writing codes.\n2. Pressing "Update preview" forces an update on the update window. This is because the tags window doesn\'t constantly update the preview with changes since you might not be finished with writing a tag.\n3. Pressing "Convert codes and copy" takes the tags you wrote, turns it into a dict and copies it to your clipboard. This lets you paste it into a Python file as is.\n4. Pressing "Copy code text" takes all the text in the code writing window and copies it to your clipboard. This lets you paste it as a string for testing or to place in any piece of code.\n\n[H2]Text code rules[H2/]\nIt\'s not necessary, but it\'s recommended to make all the codes in all caps to make them distinct from normal text.\nMake sure there aren\'t any spaces in the text code name, this can lead to ambiguity in the text code name.\nAgain, these text codes should be written like normal variables in Python.\n\nOnce you write the text code name, you can have any number of spaces, an equals sign, any number of spaces, and then an opening single or double quote followed by your text and the accompanying closing quote.\nAgain, like Python, if you want double quotes in the text code, you can use single quotes for the opening and closing quotes, and for single quotes in the text code, use double quotes.\nBut also like in Python, you can use \\" or \\\' to make sure that the quote is rendered properly and avoids bugs.\n\nFinally, if the text code is getting too long, you can make a break the string into 2 lines with a backslash.\nThis doesn\'t add a newline character, and the code interpretes the string as unbroken. Again, spaces between the closing quote and backslash don\'t matter, like in regular Python.\nExample:\nLONG_THING = "This sentence is pretty long" \\\n", so let\'s break it into 2 lines"\n\nThe code would interpret this as "This sentence is pretty long, so let\'s break it into 2 lines" with no newline characters added.\n\nAlso like regular Python strings, you can also have escape codes, like your usual \\t, \\n, \\\\, \\\', and \\". You can also just type \\ instead of \\\\ as long as the next character isn\'t part of the escape characters, because you might get accidental escape characters you didn\'t mean for.\n\n\n[/TAB][H1]Text preview area:[H1/]\nIt has the title "Formatted text preview" and this is where the preview of the formatting appears.\n\nWhatever you type in the "Formatted text writer" area is shown here with the formatting tags and text codes changing the text accordingly.\n\nThere is more info in the section about the text writer window in the "Main text writing area" chapter, but when there\'s an error with the formatting tags, the background in this window turns red. And when there\'s a warning, it turns yellow.\n\nThere are 2 checkboxes and 2 button at the top of the window that says "Do formatting", "Do text codes", and "Save text" and "Save text as"\n1. The "Do formatting" checkbox controls whether the formatting tags are used or not. If they are used, you don\'t see them in the preview and the text gets formatted. If they aren\'t used, then the tags are just placed into the preview without the formatting on the enclosed text.\n2. The "Do text codes" checkbox works similarly to the "Do formatting" one, but instead of formatting text, it\'ll be replaced by its corresponding string. So if it\'s on, then it\'ll replace the text codes, otherwise, you\'ll just see the text codes in the preview.\n3. Pressing the "Save text" button saves the guide you made in a .txt file. If the text doesn\'t have a specified file linked to it, it\'ll prompt you to give it a file name. Once it has a linked file, pressing the save button uses the same file name.\n4. Pressing the "Save text as" button works like the "Save text" button, but instead of it using the same file name once it\'s linked, it\'ll always prompt you for the file name. This can allow you to copy a text save or replace other files. But doing this will change the linked file that the current edited text is one\n\n\n[/TAB][H1]General info[H1/]\nWhen opening the program for the first time, there will be example text in each text input window to show what the format and structure looks like.\n\n\n[/TAB][H1]Shortcuts:[H1/]\n[H2]Intro[H2/]\nEach sub-heading in this chapter will be the domain where the following shortcuts work. So a sub-heading that says "Formatted text writer", then the following shortcuts only work on the "Formatted text writer" window.\n\n[H2]All windows (except the help guide)[H2/]\nClosing the program:\nEscape[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Close the program\nCtrl + W[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Close the program\nCtrl + Shift + W[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Close the program\n\nProject/file management:\nCtrl + O[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Open a .txt file\nCtrl + S[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Save to .txt filee\nCtrl + Shift + S[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Save as .txt file\nCtrl + N[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Create new formatted text project\n\nWindow management:\nCtrl + Page Down[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Cycle between the windows (Order: Main, Tags, Codes, Preview, repeat)\nCtrl + Page Up[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Cycle between the windows (Order: Preview, Codes, Tags, Main, repeat)\nCtrl + Q[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Bring all the windows to the top and visible\n\nMisc:\nCtrl + P[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Update preview\n\n[H2]All text inputs[H2/]\nMost of the shortcuts here work like in most text editors and especially like VS code\n\nText history:\nCtrl + Z[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Undo\nCtrl + Shift + Z[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Redo\nCtrl + Y[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Redo\n\nText deletion:\nCtrl + Backspace[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB] Delete a word to the left\nCtrl + Delete[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Delete a word to the right\n\nText navigation:\nLeft arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one character to the left\nRight arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one character to the right\nUp arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one line up\nDown arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one line down\nCtrl + Left arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one word to the left\nCtrl + Right arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one word to the right\nCtrl + Up arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Scroll the text up by 1 line\nCtrl + Down arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Scroll the text down by 1 line\n\nText selection:\nShift + Left arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one character to the left and change the selection\nShift + Right arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one character to the right and change the selection\nCtrl + Shift + Left arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one word to the left and change the selection\nCtrl + Shift + Right arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one word to the right and change the selection\nShift + Up arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one line up and change the selection\nShift + Down arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor one line down and change the selection\nDouble left click[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Selects the entire word that was double clicked on\nShift + Left click[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Selects everything from where the cursor started to where the mouse clicked\nShift + Home[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor to the beginning of the line and change the selection\nShift + End[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the cursor to the end of the line and change the selection\n\nText moving:\nAlt + Up arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the selected line(s) up by one line, shifting everything else down\nAlt + Down arrow[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Move the selected line(s) down  by one line, shifting everything else up\n\n[H2]Formatted text writer[H2/]\nButton shortcuts:\nCtrl + 1[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 1 (Loading text)\nCtrl + 2[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 2 (New text)\nCtrl + 3[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 3 (Help)\nCtrl + 4[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 4 (Clear text)\nCtrl + 5[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 5 (Copy text)\n\n[H2]Help guide[H2/]\nThis is a window that only opens with the "Help" button in the "Formatted text writer" window\n\nClosing the program:\nEscape[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Close the help guide\nCtrl + W[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Close the help guide\nCtrl + Shift + W[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Close the program\n\n[H2]Formatted text formatting[H2/]\nButton shortcuts:\nCtrl + 1[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 1 (Clear tags)\nCtrl + 2[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 2 (Update preview)\nCtrl + 3[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 3 (Convert tags and copy)\nCtrl + 4[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 4 (Copy tag text)\n\n[H2]Formatted text codes[H2/]\nButton shortcuts:\nCtrl + 1[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 1 (Clear codes)\nCtrl + 2[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 2 (Update preview)\nCtrl + 3[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 3 (Convert codes and copy)\nCtrl + 4[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 4 (Copy code text)\n\n[H2]Formatted text preview[H2/]\nButton/checkbox shortcuts:\nCtrl + 1[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Checkbox 1 (Do formatting)\nCtrl + 2[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Checkbox 2 (Do text codes)\nCtrl + 3[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 1 (Save text)\nCtrl + 4[/TRUE_TAB][/TRUE_TAB][/TRUE_TAB]- Button 2 (Save text as)"""
TAGS_FOR_HELP_GUIDE = {'TRUE_SUBSCRIPT': {'font': ('Arial', 8), 'offset': -3}, 'BOLD': {'font': ('Arial', 11, 'bold')}, 'H1': {'font': ('Arial', 15, 'bold')}, 'H2': {'font': ('Arial', 13, 'bold')}, 'HYPERLINK': {'foreground': 'blue', 'underline': 'True'}}
CODES_FOR_HELP_GUIDE = {'TAB': '     ', 'TRUE_TAB': '\t', 'TRUE_COORD_I': '(x[TRUE_SUBSCRIPT]i[TRUE_SUBSCRIPT/], y[TRUE_SUBSCRIPT]i[TRUE_SUBSCRIPT/])'}

USE_EXAMPLES = True
EXAMPLE_TEXT = """Basic example:\nThis is some example text!\n\n\nFormatting tag example:\n[RED]This text is red[RED/]\n\n[BOLD]This text is bold[BOLD/]\n\nThis text is [SUBSCRIPT]subscripted[SUBSCRIPT/]\n\n\nText code example:\n[/TEXT_CODE_EXAMPLE]\n\n[/TEXT_CODE_EXAMPLE_2_LINE]\n\n[/TEXT_CODE_EXAMPLE_3_LINE]\n\n[/TEXT_CODE_EXAMPLE_TRIPLE_QUOTES_A]\n\n[/TEXT_CODE_EXAMPLE_TRIPLE_QUOTES_B]\n\n[/TRIPLE_QUOTES_MULTI_LINED]"""
EXAMPLE_TAGS = """RED = { foreground: red }\n\nBOLD = { font: (Arial, 11, bold) }\n\nSUBSCRIPT = {\nfont: (Arial, 8),\noffset: -3,\n}"""
EXAMPLE_CODES = """TEXT_CODE_EXAMPLE = "This text is using a text code"\n\nTEXT_CODE_EXAMPLE_2_LINE = "This string is split into"\\\n" 2 lines using a backslash"\n\nTEXT_CODE_EXAMPLE_3_LINE = "And this string is split into"\\\n" 3 lines using a backslash!"\\\n" Isn\'t that cool?"\n\nTEXT_CODE_EXAMPLE_TRIPLE_QUOTES_A = \"\"\"Check out these cool\ntriple quotes!\"\"\"\n\nTEXT_CODE_EXAMPLE_TRIPLE_QUOTES_B = \"\"\"Triple quotes can be used\non multiple lines\nwhich is handy for long strings\nbut they do add newline chars in between each line\nyou can also write \' and " without any problems\"\"\"\n\n\nTRIPLE_QUOTES_MULTI_LINED = \"\"\"You can also use backslashes on\"\"\"\\\n" triple quotes" """


# Helper funcs
def is_valid_var_name(
    self: FormattedTextWriter,
    var_name: str,
    do_errors: bool,
    var_type: Literal["Text code", "Formatting tag"],
    type_name: str = "Var name",
) -> bool:
    if var_type not in ["Text code", "Formatting tag"]:
        raise ValueError(f"var_type must be either 'Text code' or 'Formatting tag', not '{var_type}'")

    # Check the beginning
    if var_name[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_":
        if do_errors:
            last_important_view_idx = self.current_important_view
            messagebox.showerror(var_type, f"{type_name} '{var_name}' is invalid because it starts with '{var_name[0]}'")
            self.focus_on_window_with_idx(last_important_view_idx)

        return False

    # Check the entire name
    for char in var_name:
        if char == " ":
            if do_errors:
                last_important_view_idx = self.current_important_view
                messagebox.showerror(var_type, f"{type_name} '{var_name}' is invalid because it contains space(s)")
                self.focus_on_window_with_idx(last_important_view_idx)

            return False

        if char.upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789":
            if do_errors:
                last_important_view_idx = self.current_important_view
                messagebox.showerror(var_type, f"{type_name} '{var_name}' is invalid because it contains '{char}'")
                self.focus_on_window_with_idx(last_important_view_idx)

            return False

    return True


def toggle_using_triple_quotes(
    self: FormattedTextWriter, line: str, do_errors: bool, var_type: Literal["Text code", "Formatting tag"]
) -> tuple[bool, bool]:
    if var_type not in ["Text code", "Formatting tag"]:
        raise ValueError(f"var_type must be either 'Text code' or 'Formatting tag', not '{var_type}'")

    line_idx = 0
    triple_quotes_seen = 0

    while line_idx < len(line):
        if line[line_idx : line_idx + 3] == '"""':
            triple_quotes_seen += 1
            line_idx += 2

        if line[line_idx] == "\\":
            triple_quotes_seen = 0

        if triple_quotes_seen == 3:
            if do_errors:
                last_important_view_idx = self.current_important_view
                messagebox.showerror(var_type, f"Line '{line}' has invalid triple quote usage")
                self.focus_on_window_with_idx(last_important_view_idx)

            return False, True

        line_idx += 1

    return triple_quotes_seen % 2 == 1, False


def make_a_single_string(line: str, cut_ends: bool = True) -> tuple[str, str]:
    var_name = line.split("=")[0]
    cut_line = line[len(var_name) + 2 : -1] if cut_ends else line[len(var_name) + 1 :]
    line_pieces = cut_line.split('"\\"')
    return var_name, "".join(line_pieces)


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
        self.text_options_frame.columnconfigure(4, weight=1)

        self.load_text_button = tk.Button(
            self.text_options_frame,
            text="Load text",
            command=self.load_text,
        )
        self.load_text_button.grid(row=0, column=0, padx=5, pady=5)

        self.new_text_button = tk.Button(
            self.text_options_frame,
            text="New text",
            command=self.new_text,
        )
        self.new_text_button.grid(row=0, column=1, padx=5, pady=5)

        self.open_help_for_writer_button = tk.Button(
            self.text_options_frame,
            text="Help",
            command=self.open_help,
        )
        self.open_help_for_writer_button.grid(row=0, column=2, padx=5, pady=5)
        self.help_window = None

        self.clear_text_button = tk.Button(
            self.text_options_frame,
            text="Clear text",
        )
        self.clear_text_button.grid(row=0, column=3, padx=5, pady=5)

        self.copy_text_button = tk.Button(
            self.text_options_frame,
            text="Copy text",
        )
        self.copy_text_button.grid(row=0, column=4, padx=5, pady=5)

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
        self.root.bind("<Control-Key-2>", lambda _event: self.new_text())
        self.root.bind("<Control-Key-3>", lambda _event: self.open_help())
        self.root.bind("<Control-Key-4>", lambda _event: self.clear_and_update(self.text_text_area))
        self.root.bind(
            "<Control-Key-5>",
            lambda _event: self.copy_txt_to_clipboard(repr(self.get_text_area_content(self.text_text_area))[1:-1]),
        )

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
        self.tags_settings_frame.columnconfigure(3, weight=1)

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

        self.copy_tag_text_button = tk.Button(
            self.tags_settings_frame,
            text="Copy tag text",
            command=lambda: self.copy_txt_to_clipboard(repr(self.get_text_area_content(self.tags_text_area))[1:-1]),
        )
        self.copy_tag_text_button.grid(row=0, column=3, padx=5, pady=5)

        self.tags_text_area = setup_text_popup_window(self.tags_window, undo=True)
        self.prev_tags_text_content = tk.StringVar(value=self.get_text_area_content(self.tags_text_area))
        self.clear_tags_button.config(command=lambda: self.clear_and_update(self.tags_text_area))
        self.bind_text_box_stuff(self.tags_text_area)
        self.tags_text_area.config(state="normal")
        self.tags_text_area.bind("<KeyRelease>", lambda _event: self.updated_text_area(idx=1, update_preview=False))

        self.tags_window.bind("<Control-Key-1>", lambda _event: self.clear_and_update(self.tags_text_area))
        self.tags_window.bind("<Control-Key-2>", lambda _event: self.update_preview())
        self.tags_window.bind(
            "<Control-Key-3>", lambda _event: self.copy_txt_to_clipboard(str(self.read_tags(force_read=True)))
        )
        self.tags_window.bind(
            "<Control-Key-4>",
            lambda _event: self.copy_txt_to_clipboard(repr(self.get_text_area_content(self.tags_text_area))[1:-1]),
        )

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
        self.codes_settings_frame.columnconfigure(3, weight=1)

        self.clear_codes_button = tk.Button(
            self.codes_settings_frame,
            text="Clear codes",
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

        self.copy_code_text_button = tk.Button(
            self.codes_settings_frame,
            text="Copy code text",
            command=lambda: self.copy_txt_to_clipboard(repr(self.get_text_area_content(self.codes_text_area))[1:-1]),
        )
        self.copy_code_text_button.grid(row=0, column=3, padx=5, pady=5)

        self.codes_text_area = setup_text_popup_window(self.codes_window, undo=True)
        self.prev_codes_text_content = tk.StringVar(value=self.get_text_area_content(self.codes_text_area))
        self.clear_codes_button.config(command=lambda: self.clear_and_update(self.codes_text_area))
        self.bind_text_box_stuff(self.codes_text_area)
        self.codes_text_area.config(state="normal")
        self.codes_text_area.bind("<KeyRelease>", lambda _event: self.updated_text_area(idx=2, update_preview=False))

        self.codes_window.bind("<Control-Key-1>", lambda _event: self.clear_and_update(self.codes_text_area))
        self.codes_window.bind("<Control-Key-2>", lambda _event: self.update_preview())
        self.codes_window.bind(
            "<Control-Key-3>", lambda _event: self.copy_txt_to_clipboard(str(self.read_codes(force_read=True)))
        )
        self.codes_window.bind(
            "<Control-Key-4>",
            lambda _event: self.copy_txt_to_clipboard(repr(self.get_text_area_content(self.codes_text_area))[1:-1]),
        )

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
        self.preview_settings_frame.columnconfigure(3, weight=1)

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

        #       Text preview .txt saving as
        self.save_text_button = tk.Button(
            self.preview_settings_frame,
            text="Save text as",
            command=lambda: self.save_text(save_as=True),
        )
        self.save_text_button.grid(row=0, column=3, padx=5)

        self.preview_window.bind("<Control-Key-1>", lambda _event: self.toggle_formatting())
        self.preview_window.bind("<Control-Key-2>", lambda _event: self.toggle_text_codes())
        self.preview_window.bind("<Control-Key-3>", lambda _event: self.save_text())
        self.preview_window.bind("<Control-Key-4>", lambda _event: self.save_text(save_as=True))

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

            window.bind("<Control-p>", lambda _event: self.update_preview())
            window.bind("<Control-P>", lambda _event: self.update_preview())

            window.bind("<Control-n>", lambda _event: self.new_text())
            window.bind("<Control-N>", lambda _event: self.new_text())
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

        self.text_area_list = [
            self.text_text_area,
            self.tags_text_area,
            self.codes_text_area,
        ]
        if USE_EXAMPLES:

            example_string_list = [
                EXAMPLE_TEXT,
                EXAMPLE_TAGS,
                EXAMPLE_CODES,
            ]

            for text_area, example_string in zip(self.text_area_list, example_string_list):
                clear_text_area(text_area)
                append_to_text_area(text_area, example_string)

            self.update_preview()

    def load_text(self) -> None:
        last_important_view_idx = self.current_important_view

        if not self.saved_text_progress:
            response = messagebox.askyesno(
                "Saving progress",
                "You still have unsaved work, and loading a text will overwrite everything that's written\nAre you SURE you want to continue loading?",
            )

            if not response:
                self.focus_on_window_with_idx(last_important_view_idx)
                return

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_path:
            self.focus_on_window_with_idx(last_important_view_idx)
            self.update_preview()
            self.saved_text_progress = True
            self.text_file_path = None
            for window in self.window_list:
                if window.title().endswith("*"):
                    window.title(window.title()[:-1])
            return

        content_lines = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content_lines = [line.strip() for line in f.readlines()]
        except Exception as e:
            messagebox.showerror("File loading", f"An error was encountered while loading\nError: {e}")

            self.focus_on_window_with_idx(last_important_view_idx)
            return

        full_filename = os.path.basename(file_path)

        try:
            text_content_idx = content_lines.index(f"TEXT_CONTENT_OF_{full_filename}:")
            tag_content_idx = content_lines.index(f"TAG_CONTENT_OF_{full_filename}:")
            code_content_idx = content_lines.index(f"CODE_CONTENT_OF_{full_filename}:")

        except ValueError as e:
            messagebox.showerror(
                "File loading",
                "This is an invalid save file!\nSave files cannot be made or edited in any way"
                "\nexcept for saving in the program",
            )

            self.reset_prev_text()
            self.focus_on_window_with_idx(last_important_view_idx)
            return
        except Exception as e:
            messagebox.showerror(
                "File loading",
                f"An unknown error has occurred.\nIf you are not the maintainer of this project, let them know about this bug\nError: {e}",
            )

            self.focus_on_window_with_idx(last_important_view_idx)
            return

        loaded_text_content = "\n".join(content_lines[text_content_idx + 2 : tag_content_idx - 3])
        loaded_tag_content = "\n".join(content_lines[tag_content_idx + 2 : code_content_idx - 3])
        loaded_code_content = "\n".join(content_lines[code_content_idx + 2 : -1])

        all_loaded_content = [loaded_text_content, loaded_tag_content, loaded_code_content]

        for text_area, loaded_content in zip(self.text_area_list, all_loaded_content):
            clear_text_area(text_area)
            append_to_text_area(text_area, loaded_content)

        self.update_preview()
        self.saved_text_progress = True
        self.text_file_path = file_path

        for window in self.window_list:
            if window.title().endswith("*"):
                window.title(window.title()[:-1])

        self.preview_text_area.yview("1.0")

        self.focus_on_window_with_idx(last_important_view_idx)

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
                self.focus_on_window_with_idx(last_important_view_idx)
                return
        else:
            file_path = self.text_file_path

        tag_text = self.get_text_area_content(self.tags_text_area)
        code_text = self.get_text_area_content(self.codes_text_area)

        if not self.parse_tags(tag_text, do_errors=False)[0]:
            tag_text = self.prev_tags_text_content.get()
        if not self.parse_codes(code_text, do_errors=False)[0]:
            code_text = self.prev_codes_text_content.get()

        full_filename = os.path.basename(file_path)
        full_txt_content = [
            f"TEXT_CONTENT_OF_{full_filename}:",
            '"""',
            self.get_text_area_content(self.text_text_area),
            '"""',
            "\n",
            f"TAG_CONTENT_OF_{full_filename}:",
            '"""',
            tag_text,
            '"""',
            "\n",
            f"CODE_CONTENT_OF_{full_filename}:",
            '"""',
            code_text,
            '"""',
        ]
        if not self.save_txt_file(file_path, "\n".join(full_txt_content), show_success=False):
            self.focus_on_window_with_idx(last_important_view_idx)
            return

        self.update_preview()

        self.saved_text_progress = True
        self.text_file_path = file_path

        for window in self.window_list:
            if window.title().endswith("*"):
                window.title(window.title()[:-1])

        self.focus_on_window_with_idx(last_important_view_idx)

    def new_text(self) -> None:
        last_important_view_idx = self.current_important_view

        if not self.saved_text_progress:
            response = messagebox.askyesno(
                "Saving progress",
                "You still have unsaved work, and creating a new a text will erase everything that's written\nAre you SURE you want to continue creating a new text?",
            )

            if not response:
                self.focus_on_window_with_idx(last_important_view_idx)
                return

        for text_area in self.text_area_list:
            clear_text_area(text_area)

        self.update_preview()
        self.saved_text_progress = True
        self.text_file_path = None

        for window in self.window_list:
            if window.title().endswith("*"):
                window.title(window.title()[:-1])

        self.preview_text_area.yview("1.0")

        self.focus_on_window_with_idx(last_important_view_idx)

    def read_tags(self, force_read: bool = False) -> dict[str, dict[str, Any]]:
        if not self.do_formatting_var.get() and not force_read:
            return {}

        successful, tags = self.parse_tags(self.get_text_area_content(self.tags_text_area))
        if not successful:
            return self.parse_tags(self.prev_tags_text_content.get())[1]

        return tags

    def parse_tags(self, tag_text: str, do_errors: bool = True) -> tuple[bool, dict[str, dict[str, Any]]]:
        def is_var_declaration_line(line: str, opened_braces: int) -> bool:
            if opened_braces != 0:
                return False

            equal_idx = len(line)
            open_brace_idx = -1

            for idx in range(len(line)):
                char = line[idx]

                if char == "=":
                    equal_idx = idx
                elif char == "{":
                    open_brace_idx = idx

                if equal_idx != len(line) and open_brace_idx != -1:
                    break

            return equal_idx < open_brace_idx

        def opened_brace_and_parenthesis_count_delta(
            line: str, var_name: str, group_stack: list[str], group_inverter: dict[str, str], do_errors: bool
        ) -> int:
            open_braces = 0
            open_parentheses = 0

            line_idx = 0

            single_quotes_seen = 0
            double_quotes_seen = 0
            triple_quotes_seen = 0

            while line_idx < len(line):
                if line[line_idx] == "'" and double_quotes_seen == 0 and triple_quotes_seen == 0:
                    single_quotes_seen += 1
                elif line[line_idx] == '"' and single_quotes_seen == 0:
                    if line[line_idx : line_idx + 3] == '"""' and double_quotes_seen == 0:
                        triple_quotes_seen += 1
                        line_idx += 2
                    elif triple_quotes_seen == 0:
                        double_quotes_seen += 1

                if single_quotes_seen == 3 or double_quotes_seen == 3 or triple_quotes_seen == 3:
                    single_quotes_seen = single_quotes_seen % 2
                    double_quotes_seen = double_quotes_seen % 2
                    triple_quotes_seen = triple_quotes_seen % 2

                if (line[line_idx] in {"\\", ",", ":"}) and (
                    single_quotes_seen == 2 or double_quotes_seen == 2 or triple_quotes_seen == 2
                ):
                    single_quotes_seen = 0
                    double_quotes_seen = 0
                    triple_quotes_seen = 0

                if not (single_quotes_seen == 1 or double_quotes_seen == 1 or triple_quotes_seen == 1):
                    if line[line_idx] == "{":
                        open_braces += 1
                        group_stack.append(group_inverter["{"])
                    elif line[line_idx] == "}":
                        open_braces -= 1
                        if "}" != group_stack.pop():
                            if do_errors:
                                last_important_view_idx = self.current_important_view
                                messagebox.showerror(
                                    "Formatting tag",
                                    f"Var '{var_name}' has a closing brace before closing an open parenthesis",
                                )
                                self.focus_on_window_with_idx(last_important_view_idx)

                            return 0, 0, True
                    if line[line_idx] == "(":
                        open_parentheses += 1
                        group_stack.append(group_inverter["("])
                    elif line[line_idx] == ")":
                        open_parentheses -= 1
                        if ")" != group_stack.pop():
                            if do_errors:
                                last_important_view_idx = self.current_important_view
                                messagebox.showerror(
                                    "Formatting tag",
                                    f"Var '{var_name}' has a closing parenthesis before closing an open brace",
                                )
                                self.focus_on_window_with_idx(last_important_view_idx)

                            return 0, 0, True

                line_idx += 1

            return open_braces, open_parentheses, False

        def opening_and_closing_bracket_errors(
            last_var_name: str, open_bracket_count: int, singular_bracket_type: str, plural_bracket_type: str
        ) -> None:
            last_important_view_idx = self.current_important_view
            messagebox.showerror(
                "Formatting tag",
                f"Tag '{last_var_name}' has {abs(open_bracket_count)} missing {"opening" if open_bracket_count < 0 else "closing"} {plural_bracket_type if abs(open_bracket_count) > 1 else singular_bracket_type}",
            )
            self.focus_on_window_with_idx(last_important_view_idx)

        def full_parse_string(line: str, do_errors: bool) -> tuple[str, bool]:
            line_chars = []

            single_quotes_seen = 0
            double_quotes_seen = 0
            triple_quotes_seen = 0

            just_saw = {
                "\\": False,
                ",": False,
                ":": False,
            }

            char_to_name = {
                "\\": "backslash",
                ",": "comma",
                ":": "colon",
            }

            line_idx = 0
            while line_idx < len(line):
                if (single_quotes_seen == 2 or double_quotes_seen == 2 or triple_quotes_seen == 2) and line[line_idx] in [
                    "'",
                    '"',
                ]:
                    if do_errors:
                        last_important_view_idx = self.current_important_view
                        messagebox.showerror("Formatting tag", f"Line '{line}' is missing a backslash between quotes")
                        self.focus_on_window_with_idx(last_important_view_idx)

                    return "", True

                if line[line_idx] == "'" and double_quotes_seen == 0 and triple_quotes_seen == 0:
                    single_quotes_seen += 1
                    for key in just_saw:
                        just_saw[key] = False
                elif line[line_idx] == '"' and single_quotes_seen == 0:
                    if line[line_idx : line_idx + 3] == '"""' and double_quotes_seen == 0:
                        triple_quotes_seen += 1
                        for key in just_saw:
                            just_saw[key] = False
                        line_idx += 2
                    elif triple_quotes_seen == 0:
                        double_quotes_seen += 1
                        for key in just_saw:
                            just_saw[key] = False

                if line[line_idx] in {"\\", ",", ":"}:
                    if line_chars[-1] in {"\\", ",", ":"}:
                        if do_errors:
                            last_important_view_idx = self.current_important_view
                            messagebox.showerror(
                                "Formatting tag", f"Line '{line}' has at least 2 of ['\\', ',', ':'] in a row"
                            )
                            self.focus_on_window_with_idx(last_important_view_idx)

                        return "", True

                    if single_quotes_seen == 2 or double_quotes_seen == 2 or triple_quotes_seen == 2:
                        if just_saw[line[line_idx]]:
                            if do_errors:
                                last_important_view_idx = self.current_important_view
                                messagebox.showerror(
                                    "Formatting tag", f"Line '{line}' has at least 2 {char_to_name[line[line_idx]]} in a row"
                                )
                                self.focus_on_window_with_idx(last_important_view_idx)

                            return "", True

                        just_saw[line[line_idx]]
                        single_quotes_seen = 0
                        double_quotes_seen = 0
                        triple_quotes_seen = 0

                    elif (
                        single_quotes_seen % 2 == 0
                        and double_quotes_seen % 2 == 0
                        and triple_quotes_seen % 2 == 0
                        and line[line_idx] == "\\"
                    ):
                        if do_errors:
                            last_important_view_idx = self.current_important_view
                            messagebox.showerror(
                                "Formatting tag",
                                f"Line '{line}' has a backslash outside of a string and not in between 2 strings",
                            )
                            self.focus_on_window_with_idx(last_important_view_idx)

                        return "", True

                if single_quotes_seen == 3 or double_quotes_seen == 3 or triple_quotes_seen == 3:
                    if do_errors:
                        last_important_view_idx = self.current_important_view
                        messagebox.showerror(
                            "Formatting tag",
                            f"Line '{line}' is missing a backslash for a quote escape character, a comma,\na colon, or a backslash between string pieces",
                        )
                        self.focus_on_window_with_idx(last_important_view_idx)

                    return "", True

                if (
                    line[line_idx].strip() != ""
                    or single_quotes_seen == 1
                    or double_quotes_seen == 1
                    or triple_quotes_seen == 1
                ):
                    special_escape = {
                        "n": "\n",
                        "t": "\t",
                        "\\": "\\",
                    }
                    if (
                        line_idx < len(line) - 1
                        and line[line_idx] == "\\"
                        and (single_quotes_seen == 1 or double_quotes_seen == 1 or triple_quotes_seen == 1)
                    ):
                        if line[line_idx + 1] in ['"', "'"] + list(special_escape.keys()):
                            line_chars.append(special_escape.get(line[line_idx], line[line_idx]))
                        else:
                            line_chars.append("\\")
                            line_chars.append(line[line_idx + 1])
                        line_idx += 1
                    else:
                        if line[line_idx] == "'" and single_quotes_seen == 0 and double_quotes_seen == 0 and triple_quotes_seen == 0:
                            line_chars.append('"')
                        else:
                            line_chars.append(line[line_idx])

                line_idx += 1

            if line[-1] == "\\":
                if do_errors:
                    last_important_view_idx = self.current_important_view
                    messagebox.showerror(
                        "Formatting tag",
                        f"Line '{line}' has a backslashes outside of a string and not in between 2 strings",
                    )
                    self.focus_on_window_with_idx(last_important_view_idx)

                return "", True

            if single_quotes_seen % 2 != 0 or double_quotes_seen % 2 != 0 or triple_quotes_seen % 2 != 0:
                if do_errors:
                    last_important_view_idx = self.current_important_view
                    messagebox.showerror("Formatting tag", f"Line '{line}' has quotes left unclosed")
                    self.focus_on_window_with_idx(last_important_view_idx)

                return "", True

            return "".join(line_chars), False

        def add_implicit_quotes(line: str) -> str:
            line_pieces = []

            var_name = line.split("=")[0]
            line_pieces.append(var_name)
            line_pieces.append("=")

            line_idx = len(var_name) + 1
            string_start = -1

            in_string = False

            while line_idx < len(line):
                if line[line_idx].upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789":
                    if string_start == -1 and not in_string:
                        string_start = line_idx
                else:
                    if string_start != -1:
                        attribute_name = line[string_start:line_idx]
                        valid_attribute_name = is_valid_var_name(
                            self, attribute_name, False, "Formatting tag", type_name="Attribute name"
                        )

                        if valid_attribute_name:
                            line_pieces.append('"')
                        line_pieces.append(attribute_name)
                        if valid_attribute_name:
                            line_pieces.append('"')

                        string_start = -1

                if string_start == -1:
                    line_pieces.append(line[line_idx])

                if line[line_idx] == '"':
                    in_string = not in_string

                line_idx += 1

            return "".join(line_pieces)

        # Get naive lines
        naive_lines: list[str] = []
        for line in tag_text.split("\n"):
            stripped_naive_line = line.strip()
            if stripped_naive_line != "":
                naive_lines.append(stripped_naive_line)

        # Get var lines
        var_lines: list[str] = []
        var_line_idx = -1
        open_brace_count = 0
        open_parentheses_count = 0
        parentheses_brace_stack = []
        one_group_to_another = {"(": ")", "{": "}"}
        using_triple_quotes = False
        for naive_line in naive_lines:
            if is_var_declaration_line(naive_line, open_brace_count):
                if open_brace_count != 0:
                    if do_errors:
                        last_var_name = var_lines[var_line_idx].split("=")[0].strip()
                        opening_and_closing_bracket_errors(last_var_name, open_brace_count, "brace", "braces")

                    return False, {}

                if open_parentheses_count != 0:
                    if do_errors:
                        last_var_name = var_lines[var_line_idx].split("=")[0].strip()
                        opening_and_closing_bracket_errors(
                            last_var_name, open_parentheses_count, "parenthesis", "parentheses"
                        )

                    return False, {}

                if not is_valid_var_name(self, naive_line.split("=")[0].strip(), do_errors, "Formatting tag"):
                    return False, {}

                var_lines.append(naive_line)
                var_line_idx += 1
            else:
                if using_triple_quotes:
                    var_lines[var_line_idx] += "\n"
                var_lines[var_line_idx] += naive_line

            brace_delta, parenthesis_delta, has_error = opened_brace_and_parenthesis_count_delta(
                naive_line,
                var_lines[var_line_idx].split("=")[0].strip(),
                parentheses_brace_stack,
                one_group_to_another,
                do_errors,
            )
            if has_error:
                return False, {}

            open_brace_count += brace_delta
            open_parentheses_count += parenthesis_delta

            toggle_using, has_error = toggle_using_triple_quotes(self, naive_line, do_errors, "Formatting tag")
            if has_error:
                return False, {}

            if toggle_using:
                using_triple_quotes = not using_triple_quotes

        if open_brace_count != 0:
            if do_errors:
                last_var_name = var_lines[var_line_idx].split("=")[0].strip()
                opening_and_closing_bracket_errors(last_var_name, open_brace_count, "brace", "braces")

            return False, {}

        if open_parentheses_count != 0:
            if do_errors:
                last_var_name = var_lines[var_line_idx].split("=")[0].strip()
                opening_and_closing_bracket_errors(last_var_name, open_parentheses_count, "parenthesis", "parentheses")

            return False, {}

        # Parse strings
        parsed_string_var_lines: list[str] = []
        for var_line in var_lines:
            parsed_var_line, has_error = full_parse_string(var_line, do_errors)
            if has_error:
                return False, {}

            parsed_string_var_lines.append("=".join(make_a_single_string(parsed_var_line, cut_ends=False)))

        # Add quotes to implicit strings
        quoted_var_lines: list[str] = []
        for var_line in parsed_string_var_lines:
            quoted_var_lines.append(add_implicit_quotes(var_line))

        # Finalized strings
        final_var_lines: list[str] = []
        for var_line in quoted_var_lines:
            final_var_lines.append("=".join(make_a_single_string(var_line, cut_ends=False)))

        # Final parsing
        final_var_vals: dict[str, dict[str, Any]] = {}
        for var_line in final_var_lines:
            var_name = var_line.split("=")[0]
            dict_part = var_line[len(var_name) + 1 :]

            final_var_vals[var_name] = parse_fundamental_or_dict_or_tuple(dict_part)

        return True, final_var_vals

    def read_codes(self, force_read: bool = False) -> dict[str, str]:
        if not self.do_text_codes_var.get() and not force_read:
            return {}

        successful, codes = self.parse_codes(self.get_text_area_content(self.codes_text_area))
        if not successful:
            return self.parse_codes(self.prev_codes_text_content.get())[1]

        return codes

    def parse_codes(self, code_text: str, do_errors: bool = True) -> tuple[bool, dict[str, str]]:
        def is_var_declaration_line(line: str) -> bool:
            equal_idx = len(line)
            single_quote_idx = -1
            double_quote_idx = -1

            for idx in range(len(line)):
                char = line[idx]

                if char == "=":
                    equal_idx = idx
                elif char == "'":
                    single_quote_idx = idx
                elif char == '"':
                    double_quote_idx = idx

                if equal_idx != len(line) and (single_quote_idx != -1 or double_quote_idx != -1):
                    break

            return equal_idx < single_quote_idx or equal_idx < double_quote_idx

        def full_parse_string(line: str, do_errors: bool) -> tuple[str, bool]:
            line_chars = []

            single_quotes_seen = 0
            double_quotes_seen = 0
            triple_quotes_seen = 0

            just_saw_backslash = False

            line_idx = 0
            while line_idx < len(line):
                if (single_quotes_seen == 2 or double_quotes_seen == 2 or triple_quotes_seen == 2) and line[line_idx] in [
                    "'",
                    '"',
                ]:
                    if do_errors:
                        last_important_view_idx = self.current_important_view
                        messagebox.showerror("Text code", f"Line '{line}' is missing a backslash between quotes")
                        self.focus_on_window_with_idx(last_important_view_idx)

                    return "", True

                if line[line_idx] == "'" and double_quotes_seen == 0 and triple_quotes_seen == 0:
                    single_quotes_seen += 1
                    just_saw_backslash = False
                elif line[line_idx] == '"' and single_quotes_seen == 0:
                    if line[line_idx : line_idx + 3] == '"""' and double_quotes_seen == 0:
                        triple_quotes_seen += 1
                        just_saw_backslash = False
                        line_idx += 2
                    elif triple_quotes_seen == 0:
                        double_quotes_seen += 1
                        just_saw_backslash = False

                if line[line_idx] == "\\":
                    if single_quotes_seen == 2 or double_quotes_seen == 2 or triple_quotes_seen == 2:
                        if just_saw_backslash:
                            if do_errors:
                                last_important_view_idx = self.current_important_view
                                messagebox.showerror("Text code", f"Line '{line}' has 2 backslashes in a row")
                                self.focus_on_window_with_idx(last_important_view_idx)

                            return "", True

                        just_saw_backslash = True
                        single_quotes_seen = 0
                        double_quotes_seen = 0
                        triple_quotes_seen = 0

                    elif single_quotes_seen % 2 == 0 and double_quotes_seen % 2 == 0 and triple_quotes_seen % 2 == 0:
                        if do_errors:
                            last_important_view_idx = self.current_important_view
                            messagebox.showerror(
                                "Text code",
                                f"Line '{line}' has a backslash outside of a string and not in between 2 strings",
                            )
                            self.focus_on_window_with_idx(last_important_view_idx)

                        return "", True

                if single_quotes_seen == 3 or double_quotes_seen == 3 or triple_quotes_seen == 3:
                    if do_errors:
                        last_important_view_idx = self.current_important_view
                        messagebox.showerror(
                            "Text code",
                            f"Line '{line}' is missing a backslash for a quote escape character\nor a backslash between string pieces",
                        )
                        self.focus_on_window_with_idx(last_important_view_idx)

                    return "", True

                if (
                    line[line_idx].strip() != ""
                    or single_quotes_seen == 1
                    or double_quotes_seen == 1
                    or triple_quotes_seen == 1
                ):
                    special_escape = {
                        "n": "\n",
                        "t": "\t",
                        "\\": "\\",
                    }
                    if (
                        line_idx < len(line) - 1
                        and line[line_idx] == "\\"
                        and (single_quotes_seen == 1 or double_quotes_seen == 1 or triple_quotes_seen == 1)
                    ):
                        if line[line_idx + 1] in ['"', "'"] + list(special_escape.keys()):
                            line_chars.append(special_escape.get(line[line_idx + 1], line[line_idx + 1]))
                        else:
                            line_chars.append("\\")
                            line_chars.append(line[line_idx + 1])
                        line_idx += 1
                    else:
                        if line[line_idx] == "'" and single_quotes_seen == 0 and double_quotes_seen == 0 and triple_quotes_seen == 0:
                            line_chars.append('"')
                        else:
                            line_chars.append(line[line_idx])

                line_idx += 1

            if line[-1] == "\\":
                if do_errors:
                    last_important_view_idx = self.current_important_view
                    messagebox.showerror(
                        "Text code",
                        f"Line '{line}' has a backslashes outside of a string and not in between 2 strings",
                    )
                    self.focus_on_window_with_idx(last_important_view_idx)

                return "", True

            if single_quotes_seen % 2 != 0 or double_quotes_seen % 2 != 0 or triple_quotes_seen % 2 != 0:
                if do_errors:
                    last_important_view_idx = self.current_important_view
                    messagebox.showerror("Text code", f"Line '{line}' has quotes left unclosed")
                    self.focus_on_window_with_idx(last_important_view_idx)

                return "", True

            return "".join(line_chars), False

        # Get naive lines
        naive_lines: list[str] = []
        for line in code_text.split("\n"):
            stripped_naive_line = line.strip()
            if stripped_naive_line != "":
                naive_lines.append(stripped_naive_line)

        # Get var lines
        var_lines: list[str] = []
        var_line_idx = -1
        using_triple_quotes = False
        for naive_line in naive_lines:
            if is_var_declaration_line(naive_line) and not using_triple_quotes:
                if not is_valid_var_name(self, naive_line.split("=")[0].strip(), do_errors, "Text code"):
                    return False, {}

                var_lines.append(naive_line)
                var_line_idx += 1
            else:
                if using_triple_quotes:
                    var_lines[var_line_idx] += "\n"
                var_lines[var_line_idx] += naive_line

            toggle_using, has_error = toggle_using_triple_quotes(self, naive_line, do_errors, "Text code")
            if has_error:
                return False, {}

            if toggle_using:
                using_triple_quotes = not using_triple_quotes

        # Final parsing
        final_var_vals: dict[str, str] = {}
        for var_line in var_lines:
            stripped_var_line, has_error = full_parse_string(var_line, do_errors)
            if has_error:
                return False, {}

            var_name, var_val = make_a_single_string(stripped_var_line)
            if var_name in final_var_vals:
                if do_errors:
                    last_important_view_idx = self.current_important_view
                    messagebox.showerror("Text code", f"Text code '{var_name}' already exists")
                    self.focus_on_window_with_idx(last_important_view_idx)

                return False, {}

            final_var_vals[var_name] = var_val

        return True, final_var_vals

    def copy_txt_to_clipboard(self, text: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def updated_text_area(
        self, idx: int | None = None, text_area: tk.Text | None = None, update_preview: bool = True
    ) -> None:
        if idx is None and text_area is None:
            raise ValueError("Both idx and text_area can't be None at the same time, only one can be None at a time")
        if idx is not None and text_area is not None:
            raise ValueError("Both idx and text_area can't be a value at the same time, only one can be an object at a time")

        prev_text_content_list = [
            self.prev_text_text_content,
            self.prev_tags_text_content,
            self.prev_codes_text_content,
        ]

        if idx is None:
            idx = self.text_area_list.index(text_area)

        if prev_text_content_list[idx].get() == self.get_text_area_content(self.text_area_list[idx]):
            return

        self.add_asterisk_to_window_idx(idx)
        self.saved_text_progress = False

        if update_preview:
            self.root.after_idle(self.update_preview)

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

        current_scroll_pos = self.preview_text_area.yview()
        top_idx = self.preview_text_area.index("@0,0")
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

        self.preview_text_area.yview_moveto(current_scroll_pos[0])

        self.scroll_to_text_diff(
            self.preview_text_area,
            self.get_text_diff_plus_buffer(
                prev_preview_text_area,
                formatted_text,
                start_num_char_buffer=10,
                increasing_mode="arithmetic",
                increase_amount=10,
            ),
            top_idx,
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

    def get_text_diff_plus_buffer(
        self,
        prev_text: str,
        new_text: str,
        start_num_char_buffer: int = 25,
        increasing_mode: Literal["geometric", "arithmetic"] = "arithmetic",
        increase_amount: int = 10,
    ) -> str:
        if start_num_char_buffer < 0:
            raise ValueError("start_num_char_buffer CANNOT be less than 0")

        if increasing_mode == "arithmetic" and increase_amount <= 0:
            raise ValueError('increase_amount CANNOT be less than or equal to 0 in "arithmetic" mode')

        if increasing_mode == "geometric" and increase_amount <= 1:
            raise ValueError('increase_amount CANNOT be less than or equal to 1 in "geometric" mode')

        if int(increase_amount) != increase_amount:
            raise ValueError("increase_amount has to be an int")

        idx = self.find_text_diff_idx(prev_text, new_text)

        if idx == -1:
            return ""

        num_char_buffer = start_num_char_buffer

        def splice_text(text: str, idx: int, buffer: int):
            if buffer <= idx <= len(text) - buffer - 1:
                return text[idx - buffer : idx + 1 + buffer]

            if idx < buffer:
                return text[: 2 * buffer + 1]

            return text[len(text) - (2 * buffer + 1) :]

        text_diff = splice_text(new_text, idx, num_char_buffer)
        while len(find_all_occurrences(new_text, text_diff)) > 1:
            if increasing_mode == "geometric":
                num_char_buffer *= increase_amount
            elif increasing_mode == "arithmetic":
                num_char_buffer += increase_amount
            else:
                raise ValueError('increasing_mode has to be either "geometric" or "arithmetic"')

            text_diff = splice_text(new_text, idx, num_char_buffer)

        return text_diff

    # AI generated (lots of debugging and going back and forth)
    def scroll_to_text_diff(self, text_area: tk.Text, changed_text: str, top_idx: str) -> None:
        if not changed_text:
            return

        # 1. Set the internal scroll state, but DO NOT call update_idletasks().
        # This keeps the view in memory without flashing it to the user's monitor.
        text_area.yview(top_idx)

        match_idx = text_area.search(changed_text, "1.0", stopindex=tk.END, exact=True)
        if not match_idx:
            return

        # Calculate the exact index where the changed text ends
        match_end_idx = f"{match_idx}+{len(changed_text)}c"

        widget_height = text_area.winfo_height()

        # The internal text_area.index("@...") queries will natively force
        # geometry updates for these specific coordinates without drawing them.
        top_screen_idx = text_area.index("@0,0")
        bottom_screen_idx = text_area.index(f"@0,{widget_height}")

        # 3. Add the "update" flag.
        # This explicitly tells Tkinter's C-backend to mathematically calculate
        # text wrapping right now, without updating the visual display.
        visible_dl = text_area.count(top_screen_idx, bottom_screen_idx, "update", "displaylines")
        max_visible_lines = visible_dl if visible_dl else 1

        # Check how many lines exist between the END of the edit and the end of the document
        lines_to_end = text_area.count(match_end_idx, "end-1c", "update", "displaylines")
        lines_below_edit = lines_to_end if lines_to_end else 0

        # 4. Bulletproof Bottom Pinning
        if lines_below_edit < max_visible_lines:
            text_area.yview_moveto(1.0)
            return

        # 5. One-Shot Mathematical Placement
        text_area.yview(match_idx)

        fraction_to_ideally_place_edit = 1 / 8
        ideal_center_y = int(widget_height * fraction_to_ideally_place_edit)

        try:
            text_area.yview_scroll(-ideal_center_y, "pixels")
        except tk.TclError:
            text_area.yview_scroll(-2, "units")

    def clear_and_update(self, text_area: tk.Text) -> None:
        clear_text_area(text_area)
        self.updated_text_area(text_area=text_area)

    def reset_prev_text(self) -> None:
        self.prev_text_text_content.set(self.get_text_area_content(self.text_text_area))

        if self.parse_tags(self.get_text_area_content(self.tags_text_area), do_errors=False)[0]:
            self.prev_tags_text_content.set(self.get_text_area_content(self.tags_text_area))

        if self.parse_codes(self.get_text_area_content(self.codes_text_area), do_errors=False)[0]:
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

    # Partially AI generated
    def text_box_ctrl_backspace(self, event: tk.Event) -> str:
        widget = event.widget

        if widget.tag_ranges("sel"):
            widget.delete("sel.first", "sel.last")
            widget.tag_remove("sel", "1.0", "end")
            return "break"

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

    # Partially AI generated
    def text_box_ctrl_delete(self, event: tk.Event) -> str:
        widget = event.widget

        if widget.tag_ranges("sel"):
            widget.delete("sel.first", "sel.last")
            widget.tag_remove("sel", "1.0", "end")
            return "break"

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
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")

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
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")

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
    def text_box_shift_left_arrow(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")
            else:
                widget.mark_set("anchor", "sel.first")

        if widget.compare("insert", ">", "1.0"):
            widget.mark_set("insert", "insert - 1 chars")

        widget.tag_remove("sel", "1.0", "end")
        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_shift_right_arrow(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")
            else:
                widget.mark_set("anchor", "sel.first")

        if widget.compare("insert", "<", "end - 1 chars"):
            widget.mark_set("insert", "insert + 1 chars")

        widget.tag_remove("sel", "1.0", "end")
        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    def text_box_left_arrow(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            if widget.compare("insert", ">", "1.0"):
                widget.mark_set("insert", "insert - 1 chars")
        else:
            widget.mark_set("insert", "sel.first")
            widget.tag_remove("sel", "1.0", "end")

        widget.see("insert")
        return "break"

    def text_box_right_arrow(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            if widget.compare("insert", "<", "end - 1 chars"):
                widget.mark_set("insert", "insert + 1 chars")
        else:
            widget.mark_set("insert", "sel.last")
            widget.tag_remove("sel", "1.0", "end")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_ctrl_up(self, event: tk.Event) -> str:
        widget = event.widget
        widget.yview_scroll(-1, "units")
        return "break"

    # AI generated
    def text_box_ctrl_down(self, event: tk.Event) -> str:
        widget = event.widget
        widget.yview_scroll(1, "units")
        return "break"

    # AI generated
    def text_box_shift_up(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")
            else:
                widget.mark_set("anchor", "sel.first")

        current_line = widget.index("insert").split(".")[0]
        if current_line == "1":
            widget.mark_set("insert", "1.0")
        else:
            widget.mark_set("insert", "insert - 1 displaylines")

        widget.tag_remove("sel", "1.0", "end")
        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_shift_down(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")
            else:
                widget.mark_set("anchor", "sel.first")

        current_line = widget.index("insert").split(".")[0]
        last_line = widget.index("end - 1 chars").split(".")[0]

        if current_line == last_line:
            widget.mark_set("insert", "end - 1 chars")
        else:
            widget.mark_set("insert", "insert + 1 displaylines")

        widget.tag_remove("sel", "1.0", "end")
        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_alt_up(self, event: tk.Event) -> str:
        widget = event.widget

        # 1. Determine which lines are affected (current cursor line or highlighted block)
        if widget.tag_ranges("sel"):
            start_index = widget.index("sel.first")
            end_index = widget.index("sel.last")
        else:
            start_index = widget.index("insert")
            end_index = start_index

        start_line = int(start_index.split(".")[0])
        end_line = int(end_index.split(".")[0])

        # If a highlight ends exactly at the start of the next line, don't drag that next line up
        if end_index.split(".")[1] == "0" and end_line > start_line:
            end_line -= 1

        if start_line <= 1:
            return "break"  # Already at the top, can't move up

        # 2. Store current cursor and anchor state so we can shift them later
        has_sel = bool(widget.tag_ranges("sel"))
        insert_line, insert_col = map(int, widget.index("insert").split("."))

        anchor_pos = widget.index("anchor") if "anchor" in widget.mark_names() else None
        if anchor_pos:
            anchor_line, anchor_col = map(int, anchor_pos.split("."))

        # 3. Extract the text blocks to swap
        swap_start = f"{start_line - 1}.0"
        swap_end = f"{end_line + 1}.0"

        line_above = widget.get(swap_start, f"{start_line}.0")
        block_to_move = widget.get(f"{start_line}.0", swap_end)

        # 4. Perform the swap safely within the Undo stack
        widget.edit_separator()
        widget.delete(swap_start, swap_end)
        widget.insert(swap_start, block_to_move + line_above)
        widget.edit_separator()

        # 5. Restore cursor and selection (shifted up by 1 line)
        widget.mark_set("insert", f"{insert_line - 1}.{insert_col}")
        if anchor_pos:
            widget.mark_set("anchor", f"{anchor_line - 1}.{anchor_col}")

        if has_sel and anchor_pos:
            widget.tag_remove("sel", "1.0", "end")
            if widget.compare("insert", "<", "anchor"):
                widget.tag_add("sel", "insert", "anchor")
            elif widget.compare("insert", ">", "anchor"):
                widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_alt_down(self, event: tk.Event) -> str:
        widget = event.widget

        if widget.tag_ranges("sel"):
            start_index = widget.index("sel.first")
            end_index = widget.index("sel.last")
        else:
            start_index = widget.index("insert")
            end_index = start_index

        start_line = int(start_index.split(".")[0])
        end_line = int(end_index.split(".")[0])

        if end_index.split(".")[1] == "0" and end_line > start_line:
            end_line -= 1

        # Tkinter's absolute "end" is technically an empty phantom line past your real text.
        # We need to find the last *actual* line of text to prevent dragging text off the bottom.
        last_actual_line = int(widget.index("end - 1 chars").split(".")[0])
        if end_line >= last_actual_line:
            return "break"  # Already at the bottom, can't move down

        has_sel = bool(widget.tag_ranges("sel"))
        insert_line, insert_col = map(int, widget.index("insert").split("."))

        anchor_pos = widget.index("anchor") if "anchor" in widget.mark_names() else None
        if anchor_pos:
            anchor_line, anchor_col = map(int, anchor_pos.split("."))

        swap_start = f"{start_line}.0"
        swap_end = f"{end_line + 2}.0"

        block_to_move = widget.get(swap_start, f"{end_line + 1}.0")
        line_below = widget.get(f"{end_line + 1}.0", swap_end)

        widget.edit_separator()
        widget.delete(swap_start, swap_end)
        widget.insert(swap_start, line_below + block_to_move)
        widget.edit_separator()

        # Restore cursor and selection (shifted down by 1 line)
        widget.mark_set("insert", f"{insert_line + 1}.{insert_col}")
        if anchor_pos:
            widget.mark_set("anchor", f"{anchor_line + 1}.{anchor_col}")

        if has_sel and anchor_pos:
            widget.tag_remove("sel", "1.0", "end")
            if widget.compare("insert", "<", "anchor"):
                widget.tag_add("sel", "insert", "anchor")
            elif widget.compare("insert", ">", "anchor"):
                widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # Partially AI generated
    def text_box_shift_home(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")
            else:
                widget.mark_set("anchor", "sel.first")

        widget.mark_set("insert", "insert displaylinestart")

        widget.tag_remove("sel", "1.0", "end")
        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # Partially AI generated
    def text_box_shift_end(self, event: tk.Event) -> str:
        widget = event.widget

        if not widget.tag_ranges("sel"):
            widget.mark_set("anchor", "insert")
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")
            else:
                widget.mark_set("anchor", "sel.first")

        widget.mark_set("insert", "insert displaylineend")

        widget.tag_remove("sel", "1.0", "end")
        if widget.compare("insert", "<", "anchor"):
            widget.tag_add("sel", "insert", "anchor")
        elif widget.compare("insert", ">", "anchor"):
            widget.tag_add("sel", "anchor", "insert")

        widget.see("insert")
        return "break"

    # AI generated
    def text_box_left_click(self, event: tk.Event) -> str:
        widget = event.widget
        click_index = widget.index(f"@{event.x},{event.y}")

        widget.tag_remove("sel", "1.0", "end")
        widget.mark_set("insert", click_index)
        widget.mark_set("anchor", click_index)

        widget.focus_set()
        return "break"

    # AI generated
    def text_box_left_click_drag(self, event: tk.Event) -> str:
        widget = event.widget

        if "anchor" not in widget.mark_names():
            widget.mark_set("anchor", "insert")

        drag_index = widget.index(f"@{event.x},{event.y}")
        widget.mark_set("insert", drag_index)

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
        elif "anchor" not in widget.mark_names():
            if widget.compare("insert", "==", "sel.first"):
                widget.mark_set("anchor", "sel.last")

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

        text_area.bind("<Left>", self.text_box_left_arrow)
        text_area.bind("<Right>", self.text_box_right_arrow)
        text_area.bind("<Control-Left>", self.text_box_ctrl_left_arrow)
        text_area.bind("<Control-Right>", self.text_box_ctrl_right_arrow)
        text_area.bind("<Control-Shift-Left>", self.text_box_ctrl_shift_left_arrow)
        text_area.bind("<Control-Shift-Right>", self.text_box_ctrl_shift_right_arrow)
        text_area.bind("<Shift-Left>", self.text_box_shift_left_arrow)
        text_area.bind("<Shift-Right>", self.text_box_shift_right_arrow)

        text_area.bind("<Control-Shift-Up>", self.text_box_shift_up)
        text_area.bind("<Control-Shift-Down>", self.text_box_shift_down)
        text_area.bind("<Shift-Up>", self.text_box_shift_up)
        text_area.bind("<Shift-Down>", self.text_box_shift_down)
        text_area.bind("<Control-Up>", self.text_box_ctrl_up)
        text_area.bind("<Control-Down>", self.text_box_ctrl_down)
        text_area.bind("<Alt-Up>", self.text_box_alt_up)
        text_area.bind("<Alt-Down>", self.text_box_alt_down)

        text_area.bind("<Shift-Home>", self.text_box_shift_home)
        text_area.bind("<Shift-End>", self.text_box_shift_end)

        text_area.bind("<Button-1>", self.text_box_left_click)
        text_area.bind("<B1-Motion>", self.text_box_left_click_drag)
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
        last_important_view_idx = self.current_important_view

        if not self.saved_text_progress:
            response = messagebox.askyesno("Unsaved work", "You still have unsaved work! Are you sure you want to quit now?")

            if not response:
                self.focus_on_window_with_idx(last_important_view_idx)
                return

        self.root.destroy()

    def full_quit(self, _event=None) -> None:
        last_important_view_idx = self.current_important_view

        if not self.saved_text_progress:
            response = messagebox.askyesno("Unsaved work", "You still have unsaved work! Are you sure you want to quit now?")

            if not response:
                self.focus_on_window_with_idx(last_important_view_idx)
                return

        self.root.destroy()


if __name__ == "__main__":
    formatted_text_writer = FormattedTextWriter()
    formatted_text_writer.run_gui()
