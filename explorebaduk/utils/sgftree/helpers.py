from .kifu import Kifu
from .sgflib import SGFParser
from .utils import get_move_property


def load_sgf(path: str) -> Kifu:
    with open(path) as sgf_file:
        game_tree = SGFParser(sgf_file.read()).parse()[0]

    kifu = Kifu(19, 19)
    cursor = game_tree.cursor()

    while not cursor.atEnd:
        node = cursor.next()
        move = get_move_property(node)
        kifu.make_move(move.data[0] if move.data else "pass")

    return kifu
