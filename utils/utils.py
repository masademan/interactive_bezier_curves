from typing import Callable


def run_funcs(*funcs: Callable) -> None:
    for func in funcs:
        func()
