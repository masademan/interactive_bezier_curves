import sys
import tkinter as tk
from tkinter import messagebox

# Tags in the form "stuff before tags [TAG_NAME]stuff between tags[TAG_NAME/] stuff after tags"
# However, the opening and closing tag format can be customized
# Do make sure that the tags are in a form that you can't type by accident in your normal text
OPENING_TAG = "[{}]"
CLOSING_TAG = "[{}/]"

# tags have to be initialized in the form "tags = {[TAG]: {[CONFIG_NAME]: [CONFIG]}}"
# Ex. 'tags = {"SUBSCRIPT": {"font": ("Arial", 8), "offset": -4}, "RED": {"foreground": "red"}}'


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


def tkinter_text_tag_formatter(text_area: tk.Text, tagged_text: str, tags: dict[str, dict[str, str | tuple | int]], show_warnings_in_window: bool = False) -> None:
    text_area_state = text_area.cget("state")
    text_area.config(state="normal")

    tag_states = {tag: 0 for tag in tags}  # 0 means inactive, 1 means active

    tag_start_end_locs = {}
    formatting_error_tags = []
    for tag in tags:
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

    if formatting_error_tags:
        print("Formatting errors:", file=sys.stderr)

        for error in formatting_error_tags:
            print(f" - {error}", file=sys.stderr)

        sys.exit(-1)

    for tag, tag_config in tags.items():
        text_area.tag_config(tag, **tag_config)

    tag_warnings = ["WARNING: These mismatched tags could lead to unexpected consequences"]
    tag_stack = []

    idx = 0
    txt_buffer = []
    while idx < len(tagged_text):
        if idx in tag_start_end_locs:
            text_area.insert(tk.END, "".join(txt_buffer), [tag for tag in tags if tag_states[tag] == 1])
            txt_buffer = []
            current_tag = tag_start_end_locs[idx][0]

            if tag_start_end_locs[idx][1] == "activate":
                tag_states[current_tag] = 1
                idx += 2 + len(current_tag)
                tag_stack.append(current_tag)
            else:
                tag_states[current_tag] = 0
                idx += 3 + len(current_tag)

                last_open_tag = tag_stack.pop()
                if last_open_tag != current_tag:
                    tag_warnings.append(
                        f" - The last opening tag was '[{last_open_tag}]', but the current closing tag is '[{current_tag}/]'"
                    )
        else:
            txt_buffer.append(tagged_text[idx])
            idx += 1

    if len(tag_warnings) > 1:
        if show_warnings_in_window:
            messagebox.showwarning(
                "TAG WARNING",
                "\n".join(tag_warnings),
            )
        else:
            print("\n".join(tag_warnings), file=sys.stderr)

    text_area.insert(tk.END, "".join(txt_buffer), [tag for tag in tags if tag_states[tag] == 1])

    text_area.config(state=text_area_state)
