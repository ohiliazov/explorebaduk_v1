from config import APP_NAME, APP_VERSION
from gameplay.sgflib import Property, Node, GameTree, Cursor


def create_new_sgf(board_size: int = 19) -> Cursor:
    root_properties = [
        Property('FF', ['4']),
        Property('GM', ['1']),
        Property('SZ', [str(board_size)]),
        Property('AP', [f'{APP_NAME}:{APP_VERSION}']),
        Property('CA', ['UTF-8']),
    ]
    root_node = Node(root_properties)
    game_tree = GameTree([root_node])
    cursor = Cursor(game_tree)
    return cursor
