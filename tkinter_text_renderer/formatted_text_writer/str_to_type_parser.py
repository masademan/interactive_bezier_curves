from typing import Literal, Any


def is_int_str(str_in: str) -> bool:
    if str_in[0] not in "0123456789-":
        return False

    if str_in[0] == "-" and len(str_in) == 1:
        return False

    for char_idx in range(1, len(str_in)):
        if str_in[char_idx] not in "0123456789":
            return False

    return True


def is_float_str(str_in: str) -> bool:
    if str_in[0] not in "0123456789-":
        return False

    if str_in[0] == "-" and len(str_in) == 1:
        return False

    decimal_point_found = False
    for char_idx in range(1, len(str_in)):
        if str_in[char_idx] == ".":
            if not decimal_point_found:
                decimal_point_found = True
            else:
                return False

        if str_in[char_idx] not in "0123456789-.":
            return False

    return True


def is_bool_str(str_in: str) -> bool:
    return str_in in {"True", "False"}


def is_str_str(str_in: str) -> bool:
    return str_in[0] == str_in[1] == '"'


def is_tuple_str(str_in: str) -> bool:
    return str_in[0] == "(" and str_in[1] == ")"


def is_dict_str(str_in: str) -> bool:
    return str_in[0] == "{" and str_in[-1] == "}"


def parse_number(num_str: str) -> int | float:
    if is_int_str(num_str):
        return int(num_str)
    if is_float_str(num_str):
        return float(num_str)

    raise ValueError(f"num_str must be able to turned into a number, and num_str is '{num_str}'")


def parse_boolean(bool_str: str) -> bool:
    if not is_bool_str(bool_str):
        raise ValueError(f"bool_str must be able to turned into a boolean, and bool_str is '{bool_str}'")

    return bool_str == "True"


def parse_string(str_str: str) -> str:
    if not is_str_str(str_str):
        return str_str

    return str_str[1:-1]


def parse_fundamentals(str_in: str) -> tuple[int | float | bool | str, Literal["int", "float", "bool", "str"]]:
    if is_int_str(str_in):
        return parse_number(str_in), "int"

    if is_float_str(str_in):
        return parse_number(str_in), "float"

    if is_bool_str(str_in):
        return parse_boolean(str_in), "bool"

    return parse_string(str_in), "str"


def parse_tuple(tuple_str: str) -> tuple[Any, ...]:
    if not is_tuple_str(tuple_str):
        raise ValueError(f"tuple_str must be able to be turned into a tuple, and tuple_str is '{tuple_str}'")

    temp_tuple_list = []

    open_braces_count = 0
    open_parentheses_count = 0

    tuple_section = []
    for char_idx in range(1, len(tuple_str) - 1):
        char = tuple_str[char_idx]

        if char == "(":
            open_parentheses_count += 1
        if char == ")":
            open_parentheses_count -= 1

        if char == "{":
            open_braces_count += 1
        if char == "}":
            open_braces_count -= 1

        if char == "," and open_braces_count == 0 and open_parentheses_count == 0:
            current_unparsed_section = "".join(tuple_section)
        else:
            tuple_section.append(char)

            if char_idx == len(tuple_str) - 2:
                current_unparsed_section = "".join(tuple_section)


def parse_dict(dict_str: str) -> dict[str, Any]:
    if not is_dict_str(dict_str):
        raise ValueError(f"dict_str must be able to be turned into a dict, and dict_str is '{dict_str}'")

    parsed_dict = {}

    return {}


def parse_fundamental_or_dict_or_tuple(str_in: str) -> Any:
    if is_dict_str(str_in):
        return parse_dict(str_in)

    if is_tuple_str(str_in):
        return parse_tuple(str_in)

    return parse_fundamentals(str_in)[0]
