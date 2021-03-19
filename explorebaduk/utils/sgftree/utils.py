import re

from .constants import SGF_COORDINATES


class ParserError(Exception):
    pass


reCharsToEscape = re.compile(r"[]\\]")  # characters that need to be \escaped


def escape_text(text: str):
    """Adds backslash-escapes to property value characters that need them."""
    output = ""
    index = 0
    match = reCharsToEscape.search(text, index)

    while match:
        output = output + text[index : match.start()] + "\\" + text[match.start()]
        index = match.end()
        match = reCharsToEscape.search(text, index)

    output += text[index:]
    return output


def convert_control_chars(text):
    """Converts control characters to spaces. Override for variant behaviour."""
    return text.translate(
        str.maketrans(
            "\000\001\002\003\004\005\006\007\010\011\013\014\016\017\020"
            "\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037",
            " " * 30,
        ),
    )


def swap_substring(s: str, trans: dict) -> str:
    new_values = []
    for item in s.split(" "):
        new_values.append(trans[item] if item in trans else item)

    return " ".join(new_values)


def sgf_coord_to_int(coord: str) -> tuple:
    if len(coord) != 2:
        raise ParserError("Wrong coordinates")

    x = SGF_COORDINATES.index(coord[0])
    y = SGF_COORDINATES.index(coord[1])
    return y, x


def int_coord_to_sgf(coord: tuple) -> str:
    if len(coord) != 2:
        raise ParserError("Wrong coordinates")

    x = SGF_COORDINATES[coord[0]]
    y = SGF_COORDINATES[coord[1]]
    return f"{y}{x}"


def get_move_property(node):
    return node.get_prop("B") or node.get_prop("W")
