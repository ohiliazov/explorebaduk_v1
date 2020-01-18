from enum import IntEnum
from itertools import product
from typing import List
from typing import Tuple, Set, FrozenSet, Union

import numpy as np


class CoordinateError(Exception):
    pass


class IllegalMoveError(Exception):
    pass


class Location(IntEnum):
    BLACK = 1
    EMPTY = 0
    WHITE = -1


StoneChainType = Union[FrozenSet[tuple], Set[tuple]]
CoordinateType = Tuple[Location, tuple]


class Board:
    def __init__(
        self,
        shape: tuple = (19, 19),
        board: np.ndarray = None,
        turn: Location = Location.BLACK,
        score: dict = None,
        history: List[Tuple[np.ndarray, Location, dict]] = None,
    ):
        self._shape = shape
        self._board = np.array(board, copy=True, dtype=int)
        self._turn = turn
        self._score = score or {Location.BLACK: 0, Location.WHITE: 0}
        self._history = history.copy() if history else []
        self._illegal = set()

    def __repr__(self):
        return f"GoBoard: {len(self._history)} moves, {self.turn_color} to play"

    def __str__(self):
        print_map = {
            Location.BLACK: "○ ",
            Location.WHITE: "● ",
            Location.EMPTY: ". ",
        }
        board = ""
        for x in range(self._shape[0]):
            for y in range(self._shape[1]):
                coord = x, y
                board += print_map[self._get_loc(coord)]
            board += "\n"

        return board

    @property
    def current(self):
        return np.copy(self._board)

    @property
    def history(self):
        return self._history.copy()

    @property
    def turn(self):
        """ Current player """
        return self._turn

    @property
    def turn_color(self):
        """ Current player color """
        return "black" if self._turn is Location.BLACK else "white"

    @property
    def next_turn(self) -> int:
        """ Next player color """
        return Location.BLACK if self._turn is Location.WHITE else Location.WHITE

    def _flip_turn(self) -> None:
        """ Change turn """
        self._turn = self.next_turn

    def _add_score(self, score: int) -> None:
        """ Add captured stones to score """
        self._score[self._turn] += score

    @property
    def state(self) -> Tuple[np.ndarray, Location, dict]:
        """ Current game state
        Represented as current board position, turn and score
        """
        return np.copy(self._board), self._turn, self._score.copy()

    def _push_history(self) -> None:
        """ Add current state to game history """
        self._history.append(self.state)

    def _pop_history(self) -> None:
        """ Load previous board position """
        self._board, self._turn, self._score = self._history.pop()

    def _get_loc(self, coord: tuple) -> Location:
        """ Get location of coordinate """
        if not all([0 <= xy < 19 for xy in coord]):
            raise CoordinateError(f"Coordinate {coord} is out of bounds")
        return Location(self._board[coord])

    def _get_adjacent(self, coord0: tuple) -> CoordinateType:
        """ Get surrounding locations if possible """
        x0, y0 = coord0
        coords = (
            (x0, y0 - 1),
            (x0 + 1, y0),
            (x0, y0 + 1),
            (x0 - 1, y0),
        )

        for coord in coords:
            try:
                yield self._get_loc(coord), coord
            except CoordinateError:
                pass

    def _get_chain(self, loc: Location, coord0: tuple) -> StoneChainType:
        """ Get connected chain of stones or empty area
        :param loc: color to retrieve
        :param coord0: position to start
        :return:
        """
        explored = set()
        unexplored = {coord0}

        while unexplored:
            coord = unexplored.pop()
            unexplored |= {coord for p, coord in self._get_adjacent(coord) if p == loc}

            explored.add(coord)
            unexplored -= explored

        return frozenset(explored)

    def _get_chain_adjacent(self, loc: Location, chain: StoneChainType) -> Set[CoordinateType]:
        surrounding = set()

        for coord in chain:
            surrounding |= {coord for p, coord in self._get_adjacent(coord) if p != loc}

        return surrounding

    def _get_group(self, coord: tuple) -> StoneChainType:
        loc = self._get_loc(coord)

        if loc is Location.EMPTY:
            raise CoordinateError(f"Empty")

        return self._get_chain(loc, coord)

    def _get_area(self, coord: tuple) -> StoneChainType:
        loc = self._get_loc(coord)

        if loc is not Location.EMPTY:
            raise CoordinateError(f"Not empty")

        return self._get_chain(loc, coord)

    def _get_liberties(self, group: StoneChainType) -> Set[tuple]:
        liberties = set()

        for coord in group:
            liberties |= {coord for p, coord in self._get_adjacent(coord) if p is Location.EMPTY}

        return liberties

    def _get_one_point_area(self) -> Set[tuple]:
        unexplored = np.array(self._board == Location.EMPTY)
        moves = set()

        for coord in product(range(19), range(19)):

            if unexplored[coord]:
                area = self._get_area(coord)

                if len(area) == 1:
                    moves |= area

                unexplored[tuple(zip(*area))] = False

        return moves

    def _kill_group(self, group: StoneChainType) -> int:
        liberties = self._get_liberties(group)

        if liberties:
            return 0

        self._board[tuple(zip(*group))] = 0
        return len(group)

    def _capture(self, coord0: tuple):
        """ Remove pieces if needed """
        score = 0

        for p, coord in self._get_adjacent(coord0):
            if p == self.next_turn:
                group = self._get_group(coord)
                score += self._kill_group(group)

        return score

    def _check_suicide(self, coord: tuple):
        """ Verify that played stone has at least one liberty """

        group = self._get_group(coord)
        liberties = self._get_liberties(group)

        if not liberties:
            self._pop_history()
            raise IllegalMoveError("Suicide")

    def _check_ko(self):
        """ Verify that super ko rule is not violated """
        for history_board, turn, score in reversed(self._history):
            if np.array_equal(self._board, history_board):
                self._pop_history()
                raise IllegalMoveError("Ko")

    def _set_illegal(self):
        self._illegal = set()
        illegal = set()
        for coord in self._get_one_point_area():
            try:
                self.move(coord, False)
                self._pop_history()
            except IllegalMoveError:
                illegal.add(coord)

        self._illegal = illegal

    def move(self, coord: tuple, update_illegal: bool = True):
        if coord in self._illegal:
            raise IllegalMoveError("Illegal move")
        loc = self._get_loc(coord)

        if loc != Location.EMPTY:
            raise IllegalMoveError("Not empty")

        self._push_history()
        self._board[coord] = self._turn
        captured = self._capture(coord)

        if captured:
            self._add_score(captured)
        else:
            self._check_suicide(coord)

        self._check_ko()
        self._flip_turn()

        if update_illegal:
            self._set_illegal()

    def make_pass(self):
        self._push_history()
        self._flip_turn()

    @property
    def legal_moves(self):
        legal_moves = np.ones(self._shape, dtype=int)

        legal_moves[self.current.nonzero()] = 0

        if self._illegal:
            legal_moves[tuple(zip(*self._illegal))] = 0

        return legal_moves
