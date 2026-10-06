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
    return str_in.lower() in {"true", "false"}


def is_str_str(str_in: str) -> bool:
    return str_in[0] == str_in[-1] == '"'


def is_tuple_str(str_in: str) -> bool:
    return str_in[0] == "(" and str_in[-1] == ")"


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

    return bool_str.lower() == "true"


def parse_string(str_str: str) -> str:
    if not is_str_str(str_str):
        return str_str

    return str_str[1:-1]


def parse_fundamentals(str_in: str) -> int | float | bool | str:
    if is_int_str(str_in):
        return parse_number(str_in)

    if is_float_str(str_in):
        return parse_number(str_in)

    if is_bool_str(str_in):
        return parse_boolean(str_in)

    return parse_string(str_in)


def parse_tuple(tuple_str: str) -> tuple[int | float | bool | str | tuple | dict, ...]:
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
            if len(tuple_section) > 0:
                temp_tuple_list.append(parse_fundamental_or_dict_or_tuple("".join(tuple_section)))

            tuple_section = []
        else:
            tuple_section.append(char)

    if len(tuple_section) > 0:
        temp_tuple_list.append(parse_fundamental_or_dict_or_tuple("".join(tuple_section)))

    return tuple(temp_tuple_list)


def parse_dict(dict_str: str) -> dict[str, int | float | bool | str | tuple | dict]:
    if not is_dict_str(dict_str):
        raise ValueError(f"dict_str must be able to be turned into a dict, and dict_str is '{dict_str}'")

    parsed_dict = {}

    open_braces_count = 0
    open_parentheses_count = 0

    finding_mode: Literal["key", "value"] = "key"

    key_section = []
    value_section = []
    for char_idx in range(1, len(dict_str) - 1):
        char = dict_str[char_idx]

        if char == "(":
            open_parentheses_count += 1
        if char == ")":
            open_parentheses_count -= 1

        if char == "{":
            open_braces_count += 1
        if char == "}":
            open_braces_count -= 1

        if finding_mode == "key":
            if char == ":" and open_braces_count == 0 and open_parentheses_count == 0:
                finding_mode = "value"
            else:
                key_section.append(char)

        elif finding_mode == "value":
            if char == "," and open_braces_count == 0 and open_parentheses_count == 0:
                if len(key_section) > 0 and len(value_section) > 0:
                    parsed_key = parse_fundamental_or_dict_or_tuple("".join(key_section))
                    if type(parsed_key).__name__ == "dict":
                        raise ValueError("The key of a dict can't be another dict")

                    parsed_dict[parsed_key] = parse_fundamental_or_dict_or_tuple("".join(value_section))

                key_section = []
                value_section = []

                finding_mode = "key"
            else:
                value_section.append(char)

    if len(key_section) > 0 and len(value_section) > 0:
        parsed_key = parse_fundamental_or_dict_or_tuple("".join(key_section))
        if type(parsed_key).__name__ == "dict":
            raise ValueError("The key of a dict can't be another dict")

        parsed_dict[parsed_key] = parse_fundamental_or_dict_or_tuple("".join(value_section))

    return parsed_dict


def parse_fundamental_or_dict_or_tuple(
    str_in: str,
) -> (
    int
    | float
    | bool
    | str
    | tuple[int | float | bool | str | tuple | dict, ...]
    | dict[str, int | float | bool | str | tuple | dict]
):
    if is_dict_str(str_in):
        return parse_dict(str_in)

    if is_tuple_str(str_in):
        return parse_tuple(str_in)

    return parse_fundamentals(str_in)


if __name__ == "__main__":
    fundamental_type_tests = [
        "-1",
        "-0.5",
        "True",
        '"True"',
        "False",
        '"False"',
        "5",
        "6.5",
    ]
    print("Fundamental type test:")
    for type_test in fundamental_type_tests:
        parsed_test = parse_fundamentals(type_test)
        print(f"   '{type_test}' parses to {parsed_test} of type {type(parsed_test).__name__}")

    print()

    dict_and_tuple_type_test = [
        "(1,1)",
        "(1,(2,3))",
        "(1,((2,3),4))",
        "(1,)",
        "((1,),2,)",
        "(,,)",
        "(,,5,,)",
        "{1:1}",
        "{1:1,2:2,}",
        '{1:1,3:(1,2,3),"hi":"there"}',
        '{(1,2):3,"i like games":"me too"}',
    ]
    print("Dict and tuple type test:")
    for type_test in dict_and_tuple_type_test:
        parsed_test = parse_fundamental_or_dict_or_tuple(type_test)
        print(f"   '{type_test}' parses to {parsed_test} of type {type(parsed_test).__name__}")
