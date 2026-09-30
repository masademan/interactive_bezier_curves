import sys
import tkinter as tk
from tkinter import messagebox

# Tags in the form "stuff before tags [TAG_NAME]stuff between tags[TAG_NAME/] stuff after tags"
# However, the opening and closing tag format can be customized
# Do make sure that the tags are in a form that you can't type by accident in your normal text
OPENING_TAG = "[{}]"
CLOSING_TAG = "[{}/]"

# tags have to be initialized in the form "formatting_tags = {[TAG]: {[CONFIG_NAME]: [CONFIG]}}"
# Ex. 'formatting_tags = {"SUBSCRIPT": {"font": ("Arial", 8), "offset": -4}, "RED": {"foreground": "red"}}'


# Special text codes can also be added, like a tab code
# These codes would be in the form "[/CODE_NAME]", and can be setup in a similar way
#   as the formatting tags
# Just like the formatting codes, the text code can also be customized
# Do make sure that the codes are in a form that you can't type by accident in your normal text
TEXT_CODE = "[/{}]"

# codes have to be initialized in the form "text_codes = {[CODE_NAME]: "[TEXT_THAT_REPLACES_THE_CODE]"}"
# Ex. 'text_codes = {"TAB": "   ", "COORD": "(x, y)"}'


def find_all_occurrences(full_str: str, substring: str) -> list[int]:
    """
    Returns a list of indices where the substring can be found in full_str
    The index is pointing to where the substring starts
    """
    if len(substring) < 1:
        raise ValueError("substring must be at least 1 character long")

    idx_found_at = []

    substring_idx = 0
    for i in range(len(full_str)):
        if full_str[i] != substring[substring_idx]:
            substring_idx = 0

        if full_str[i] == substring[substring_idx]:
            substring_idx += 1

        if substring_idx == len(substring):
            idx_found_at.append(i - len(substring) + 1)
            substring_idx = 0

    return idx_found_at


def clear_text_area(text_area: tk.Text) -> None:
    text_area_state = text_area.cget("state")
    text_area.config(state="normal")
    text_area.delete("1.0", tk.END)
    text_area.config(state=text_area_state)


def tkinter_text_tag_formatter(
    text_area: tk.Text,
    tagged_text: str,
    formatting_tags: dict[str, dict[str, str | tuple | int]] = {},
    text_codes: dict[str, str] = {},
    do_formatting: bool = True,
    replace_text_codes: bool = True,
    show_errors_in_window: bool = True,
    crash_on_error: bool = True,
    show_warnings_in_window: bool = True,
) -> None:
    """
    Given a tk.Text object and some text, this will use tags to format the text given the formatting_tags dict\n
    Text codes can also be specified that get replaced with another string during rendering\n
    do_formatting can enable/disable formatting, which is good for testing\n
    replace_text_codes can also be enabled/disabled for the same reason\n
    show_errors_in_window and show_warnings_in_window both control whether or not tag errors/warnings get shown in a pop up window\n
    crash_on_error will make the program crash when it hits a tag error if true, and if false,
        it'll just write all the text without formatting\n
    """

    text_area_state = text_area.cget("state")
    text_area.config(state="normal")

    tag_states = {tag: 0 for tag in formatting_tags}  # 0 means inactive, 1 means active

    tag_start_end_locs = {}
    formatting_error_tags = []

    if do_formatting:
        for tag in formatting_tags:
            activate_idxs = find_all_occurrences(tagged_text, OPENING_TAG.format(tag))
            for idx in activate_idxs:
                tag_start_end_locs[idx] = (tag, "activate")

            deactivate_idxs = find_all_occurrences(tagged_text, CLOSING_TAG.format(tag))
            for idx in deactivate_idxs:
                tag_start_end_locs[idx] = (tag, "deactivate")

            if len(activate_idxs) > len(deactivate_idxs):
                num_missing = len(activate_idxs) - len(deactivate_idxs)
                formatting_error_tags.append(
                    f'There {"is" if num_missing == 1 else "are"} {num_missing} closing "{tag}" tags that are missing'
                )
            if len(activate_idxs) < len(deactivate_idxs):
                num_missing = len(deactivate_idxs) - len(activate_idxs)
                formatting_error_tags.append(
                    f'There {"is" if num_missing == 1 else "are"} {num_missing} opening "{tag}" tags that are missing'
                )

    text_code_locs = {}

    if replace_text_codes:
        for text_code in text_codes:
            all_idxs = find_all_occurrences(tagged_text, TEXT_CODE.format(text_code))
            for idx in all_idxs:
                text_code_locs[idx] = text_code

    if formatting_error_tags:
        error_lines = ["Formatting errors:"]

        for error in formatting_error_tags:
            error_lines.append(f" - {error}")

        if show_errors_in_window:
            messagebox.showwarning(
                "TAG ERRORS",
                "\n".join(
                    error_lines
                    + [
                        "",
                        "If you are seeing this error and you aren't a developer, then",
                        "contact the maintainer of this project to get the bug fixed",
                    ]
                ),
            )

        print("\n".join(error_lines), file=sys.stderr)

        if crash_on_error:
            sys.exit(-1)
        else:
            text_area.config(state=text_area_state)
            tkinter_text_tag_formatter(
                text_area,
                tagged_text,
                text_codes=text_codes
            )
            return

    for tag, tag_config in formatting_tags.items():
        text_area.tag_config(tag, **tag_config)

    tag_warnings = ["WARNING: These mismatched tags could lead to unexpected consequences"]
    tag_stack = []

    idx = 0
    txt_buffer = []
    while idx < len(tagged_text):
        if idx in tag_start_end_locs:
            text_area.insert(tk.END, "".join(txt_buffer), [tag for tag in formatting_tags if tag_states[tag] == 1])
            txt_buffer = []
            current_tag = tag_start_end_locs[idx][0]

            if tag_start_end_locs[idx][1] == "activate":
                tag_states[current_tag] = 1
                idx += (len(OPENING_TAG) - 2) + len(current_tag)
                tag_stack.append(current_tag)
            else:
                tag_states[current_tag] = 0
                idx += (len(CLOSING_TAG) - 2) + len(current_tag)

                last_open_tag = tag_stack.pop()
                if last_open_tag != current_tag:
                    tag_warnings.append(
                        f" - The last opening tag was '[{last_open_tag}]',\n     but the current closing tag is '[{current_tag}/]'"
                    )
        elif idx in text_code_locs:
            current_text_code = text_code_locs[idx]
            txt_buffer.append(text_codes[current_text_code])
            idx += (len(TEXT_CODE) - 2) + len(current_text_code)
        else:
            txt_buffer.append(tagged_text[idx])
            idx += 1

    if len(tag_warnings) > 1:
        if show_warnings_in_window:
            messagebox.showwarning(
                "TAG WARNING",
                "\n".join(
                    tag_warnings
                    + [
                        "",
                        "If you are seeing this error and you aren't a developer, then",
                        "contact the maintainer of this project to get the bug fixed",
                    ]
                ),
            )

        print("\n".join(tag_warnings), file=sys.stderr)

    text_area.insert(tk.END, "".join(txt_buffer), [tag for tag in formatting_tags if tag_states[tag] == 1])

    text_area.config(state=text_area_state)
