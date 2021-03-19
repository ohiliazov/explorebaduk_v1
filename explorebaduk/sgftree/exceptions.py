class EndOfDataParseError(Exception):
    """Raised by `SGFParser.parse_variations()`, `SGFParser.parseNode()`."""

    pass


class GameTreeParseError(Exception):
    """Raised by `SGFParser.parse_game_tree()`."""

    pass


class NodeParseError(Exception):
    """Raised by `SGFParser.parse_node()`."""

    pass


class PropertyParseError(Exception):
    """Raised by `SGFParser.parse_property_value()`."""

    pass


class PropertyMergeError(Exception):
    """Raised by `Property.merge()`."""

    pass


class NodeMergeError(Exception):
    """Raised by `Node.merge()`."""

    pass


class NodePropertyError(Exception):
    """Raised by `Node.add_prop()`."""

    pass


class GameTreeError(Exception):
    """Raised by `GameTree.insert_tree()`."""

    pass


class GameTreeIndexError(Exception):
    """Raised by `GameTree.get_subtree()`"""

    pass


class GameTreeNavigationError(Exception):
    """Raised by `Cursor.next()`."""

    pass


class GameTreeEndError(Exception):
    """Raised by `Cursor.next()`, `Cursor.previous()`."""

    pass
