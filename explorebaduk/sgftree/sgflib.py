import re
from typing import List, Union

from .exceptions import (
    EndOfDataParseError,
    GameTreeEndError,
    GameTreeError,
    GameTreeNavigationError,
    GameTreeParseError,
    NodeParseError,
    PropertyParseError,
)
from .utils import convert_control_chars, escape_text, get_move_property

reCharsToEscape = re.compile(r"[]\\]")  # characters that need to be \escaped
reGameTreeStart = re.compile(r"\s*\(")
reGameTreeEnd = re.compile(r"\s*\)")
reGameTreeNext = re.compile(r"\s*([;()])")
reNodeContents = re.compile(r"\s*([A-Za-z]+(?=\s*\[))")
rePropertyStart = re.compile(r"\s*\[")
rePropertyEnd = re.compile(r"\]")
reEscape = re.compile(r"\\")
reLineBreak = re.compile(r"\r\n?|\n\r?")  # CR, LF, CR/LF, LF/CR


class Property:
    """An SGF property"""

    def __init__(self, label: str, prop_values: List[Union[str, int, float]] = None):
        self.data = sorted(
            set([escape_text(str(value)) for value in prop_values or [] if value]),
        )
        self.label = label

    def __str__(self):
        """SGF representation of property"""
        return f"{self.label}[{']['.join(self.data)}]"

    def __hash__(self):
        return hash(str(self))

    def __getitem__(self, item: int) -> str:
        return self.data[item]

    def __eq__(self, other: "Property"):
        return other is not None and self.label == other.label and self.data == other.data

    def copy(self) -> "Property":
        return Property(self.label, self.data.copy())


class Node:
    """An SGF node"""

    def __init__(self, props: List[Property] = None):
        self.data = {}
        props = props or []
        for prop in props:
            if prop:
                self.add_prop(prop)

    def __str__(self):
        """SGF representation of Node"""
        values = "".join([str(prop) for prop in self.data.values()])
        return f";{values}"

    def __getitem__(self, item: str):
        return self.data[item]

    def __setitem__(self, key: str, value: Property):
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def get_prop(self, label: str):
        return self.data.get(label)

    def add_prop(self, prop: Property):
        """Adds property to the node"""
        self.data[prop.label] = prop

    def pop_prop(self, label: str):
        """Removes property from the node"""
        self.data.pop(label, None)

    def copy(self) -> "Node":
        return Node([prop.copy() for prop in self.data.values()])


class GameTree:
    """An SGF game tree"""

    def __init__(self, nodes: List[Node] = None, variations: List["GameTree"] = None):
        self.data = nodes or []
        self.variations = variations or []

        if len(self.variations) == 1:
            self.data.extend(self.variations[0])
            self.variations = []

    def __str__(self):
        """SGF representation of game tree"""
        values = "".join([str(x) for x in self.data + self.variations])
        return f"({values})"

    def __getitem__(self, item: int):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def cursor(self) -> "Cursor":
        return Cursor(self)

    def copy(self):
        return GameTree(
            [node.copy() for node in self.data],
            [tree.copy() for tree in self.variations],
        )

    def append_node(self, node: Node):
        if self.variations:
            raise GameTreeError("Tree has variations")
        self.data.append(node)

    def get_subtree(self, index: int = 0):
        if 0 <= index < len(self.data):
            return GameTree(
                self.data[index:],
                [tree.copy() for tree in self.variations],
            )

        raise GameTreeError("Invalid subtree index")

    def insert_tree(self, index: int, new_tree: "GameTree", is_main: bool = False):
        if index == 0:
            raise GameTreeError("Cannot insert tree to first node")

        if index < len(self):
            # convert part of existing tree into a subtree
            self.data, existing_tree = self.data[:index], self.get_subtree(index)
            self.variations = [new_tree, existing_tree] if is_main else [existing_tree, new_tree]

        elif self.variations:
            # we have some variations, so append new one
            if is_main:
                self.variations.insert(0, new_tree)
            else:
                self.variations.append(new_tree)

        else:
            # this is the end of game tree
            self.data.extend(new_tree.data)
            self.variations = new_tree.variations

        return self

    def cut_tree(self, index: int):
        if 0 <= index < len(self):
            self.data = self.data[:index]
            self.variations = []

        raise GameTreeError("Invalid subtree index")

    def cut_variation(self, index: int):
        self.variations.pop(index)

        if len(self.variations) == 1:
            self.data.extend(self.variations[0].data)
            self.variations = self.variations[0].variations

    def set_main_variation(self, index: int):
        if not 0 <= index < len(self.variations):
            raise GameTreeError("Variation does not exist")

        main_variation = self.variations.pop(index)
        self.variations.insert(0, main_variation)


class Cursor:
    """
    [GameTree] navigation tool. Instance attributes:
      - self.game : [GameTree] -- The root [GameTree].
      - self.game_tree : [GameTree] -- The current [GameTree].
      - self.node : [Node] -- The current Node.
      - self.node_num : integer -- The offset of [self.node] from the root [self.game].
        The node_num of the root node is 0.
      - self.index : integer -- The offset of [self.node] within [self.game_tree].
      - self.stack : list of [GameTree] -- A record of [GameTree]s traversed.
      - self.children : list of [Node] -- All child nodes of the current node.
      - self.atEnd : boolean -- Flags if we are at the end of a branch.
      - self.atStart : boolean -- Flags if we are at the start of the game."""

    def __init__(self, game_tree: GameTree):
        self.game_tree = self.game = game_tree
        self.index = 0
        self.stack = []
        self.path = []
        self._set_flags()

    def _set_flags(self):
        """Sets up the flags [self.atEnd] and [self.atStart]."""
        self.atStart = not self.stack and (self.index == 0)
        self.atSplit = (self.index + 1 == len(self.game_tree)) and bool(
            self.game_tree.variations,
        )
        self.atEnd = (self.index + 1 == len(self.game_tree)) and not self.game_tree.variations

    @property
    def node(self) -> Node:
        return self.game_tree[self.index]

    def reset(self):
        """Set 'Cursor' to point to the start of the root 'GameTree', 'self.game'."""
        self.__init__(self.game)

    def next(self, variation: int = 0):
        """
        Move to the next move

        :param variation: number of variation, used only when variations split
        """
        if self.index + 1 < len(self.game_tree):  # more main line?
            self.index += 1

        elif self.game_tree.variations:  # variations exist?

            if variation < len(self.game_tree.variations):
                self.stack.append(self.game_tree)
                self.game_tree = self.game_tree.variations[variation]
                self.index = 0
            else:
                raise GameTreeNavigationError
        else:
            raise GameTreeEndError

        self.path.append(variation)
        self._set_flags()

        return self.node

    def previous(self):
        """
        Moves the [Cursor] to the previous [Node] and returns it.
        Raises [GameTreeEndError] if the start of a branch is exceeded."""
        if self.index > 0:  # more main line?
            self.index -= 1
        elif self.stack:  # were we in a variation?
            self.game_tree = self.stack.pop()
            self.index = len(self.game_tree) - 1
        else:
            raise GameTreeEndError

        self.path.pop()
        self._set_flags()

        return self.node

    def jump_to(self, path: list):
        """Goes to specified position"""
        self.reset()

        for variation in path:
            self.next(variation)

        return self.node

    def append_node(self, node: Node, is_main: bool = False):
        node_move = get_move_property(node)
        if not self.atEnd and not self.atSplit:
            next_node_moves = [get_move_property(self.game_tree[self.index + 1])]
        else:
            next_node_moves = [get_move_property(tree[0]) for tree in self.game_tree.variations]

        if node_move not in next_node_moves:
            self.game_tree.insert_tree(
                self.index + 1,
                GameTree([node]),
                is_main=is_main,
            )
        elif is_main:
            self.game_tree.set_main_variation(next_node_moves.index(node_move))

        self._set_flags()


class SGFParser:
    """
    Parser for SGF data. Creates a tree structure based on the SGF standard itself.
    [SGFParser.parse()] will return a [Collection] object for the entire data.
    Instance attributes:
      - self.data : string -- the complete SGF data instance.
      - self.data_len : integer -- length of [self.data].
      - self.index : integer -- current parsing position in [self.data]."""

    def __init__(self, data: str):
        self.data = data
        self.data_len = len(data)
        self.index = 0

    def _match_regex(self, regex):
        return regex.match(self.data, self.index)

    def _search_regex(self, regex):
        return regex.search(self.data, self.index)

    def parse(self) -> List[GameTree]:
        """Parses SGF file contents"""

        game_trees = []
        while self.index < self.data_len:
            sgf_game = self.parse_one_game()

            if not sgf_game:
                break

            game_trees.append(sgf_game)

        return game_trees

    def parse_one_game(self) -> GameTree:
        """Starts parsing game tree when `(` encountered."""

        if self.index < self.data_len:
            match = self._match_regex(reGameTreeStart)
            if match:
                self.index = match.end()
                return self.parse_game_tree()

    def parse_game_tree(self) -> GameTree:
        """Parses game tree between matching `(` and `)`."""

        game_tree = GameTree()
        while self.index < self.data_len:
            match = self._match_regex(reGameTreeNext)
            if match:
                self.index = match.end()
                if match.group(1) == ";":  # Start of a node
                    if game_tree.variations:
                        raise GameTreeParseError(
                            "A node was encountered after a variation.",
                        )
                    game_tree.append_node(self.parse_node())
                elif match.group(1) == "(":  # Start of variation
                    game_tree.variations = self.parse_variations()
                else:  # End of GameTree ")"
                    return game_tree
            else:
                raise GameTreeParseError("Invalid SGF file format.")
        return game_tree

    def parse_variations(self) -> List[GameTree]:
        """Parses variations of the game tree between `(` and non-matching `)`."""

        variations = []
        while self.index < self.data_len:
            match = self._match_regex(
                reGameTreeEnd,
            )  # check for the `)` at end of game tree, do not consume it
            if match:
                return variations
            game_tree = self.parse_game_tree()
            if game_tree:
                variations.append(game_tree)
            match = self._match_regex(
                reGameTreeStart,
            )  # check for next variation, consume `(`
            if match:
                self.index = match.end()

        raise EndOfDataParseError

    def parse_node(self) -> Node:
        """Parses node after consuming `;`."""

        node = Node()
        while self.index < self.data_len:
            match = self._match_regex(reNodeContents)
            if match:
                self.index = match.end()
                pv_list = self.parse_property_value()
                if pv_list:
                    prop = Property(match.group(1), pv_list)
                    node.add_prop(prop)
                else:
                    raise NodeParseError
            else:  # End of Node
                return node
        raise EndOfDataParseError

    def parse_property_value(self) -> List[str]:
        """
        Parses property values between `[` and the start of
        next property, node or variation.
        """

        pv_list = []
        while self.index < self.data_len:
            match = self._match_regex(rePropertyStart)
            if match:
                self.index = match.end()
                value = ""
                m_end = self._search_regex(rePropertyEnd)
                m_escape = self._search_regex(reEscape)

                # unescape escaped characters (remove linebreaks)
                while m_escape and m_end and (m_escape.end() < m_end.end()):
                    # copy everything up to '\', remove '\'
                    value += self.data[self.index : m_escape.start()]
                    m_break = reLineBreak.match(self.data, m_escape.end())
                    if m_break:
                        # skip linebreak
                        self.index = m_break.end()
                    else:
                        # copy escaped character and move to point after it
                        value += self.data[m_escape.end()]
                        self.index = m_escape.end() + 1
                    m_end = self._search_regex(rePropertyEnd)
                    m_escape = self._search_regex(reEscape)
                if m_end:
                    value += self.data[self.index : m_end.start()]
                    self.index = m_end.end()
                    pv_list.append(convert_control_chars(value))
                else:
                    raise PropertyParseError
            else:  # end of property
                break

        return pv_list
