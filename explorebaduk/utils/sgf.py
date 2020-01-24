from config import APP_NAME, APP_VERSION
from explorebaduk.gameplay.sgflib import Property, Node, GameTree, Cursor

SGF_COORDINATES = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class ParserError(Exception):
    pass


def sgf_coord_to_int(coord: str) -> tuple:
    if len(coord) != 2:
        raise ParserError("Wrong coordinates")

    x = SGF_COORDINATES.index(coord[1])
    y = SGF_COORDINATES.index(coord[0])
    return x, y


def int_coord_to_sgf(coord: tuple) -> str:
    if len(coord) != 2:
        raise ParserError("Wrong coordinates")

    x = SGF_COORDINATES[coord[1]]
    y = SGF_COORDINATES[coord[0]]
    return f"{x}{y}"


def create_new_sgf(board_size: tuple = (19, 19)) -> Cursor:
    if board_size[0] == board_size[1]:
        size = str(board_size[0])
    else:
        size = ":".join(board_size)

    root_properties = [
        Property("FF", ["4"]),
        Property("GM", ["1"]),
        Property("SZ", [size]),
        Property("AP", [f"{APP_NAME}:{APP_VERSION}"]),
        Property("CA", ["UTF-8"]),
    ]

    root_node = Node(root_properties)
    game_tree = GameTree([root_node])
    cursor = Cursor(game_tree)
    return cursor
