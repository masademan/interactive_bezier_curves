from typing import Literal, Any

HELP_SECTIONS = [
    "Quick start",
    "Help guides",
    "Grid settings",
    "Control point settings",
    "Control point position window",
    "Bezier curve settings",
    "Controls",
    "Shortcuts",
    "Usage",
]

HELP_GUIDE_SELECTION: dict[str, dict[Literal["text", "tags", "codes"], str | dict[str, Any]]] = {
    "default": {
        "text": """""",
        "tags": {
            "SUBSCRIPT": {"font": ("Arial", 8), "offset": -3},
            "H1": {"font": ("Arial", 15, "bold")},
            "H2": {"font": ("Arial", 13, "bold")},
            "HYPERLINK": {"foreground": "blue", "underline": "True"},
            "UNDERLINE": {"underline": "True"},
            "STRIKETHROUGH": {"overstrike": "True"},
            "BOLD": {"font": ("Arial", 11, "bold")},
            "ITALIC": {"font": ("Arial", 11, "italic")},
            "RED": {"foreground": "red"},
        },
        "codes": {},
    },
    "Quick start": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Help guides": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Grid settings": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Control point settings": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Control point position window": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Bezier curve settings": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Controls": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Shortcuts": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
    "Usage": {
        "text": """""",
        "tags": {},
        "codes": {},
    },
}
