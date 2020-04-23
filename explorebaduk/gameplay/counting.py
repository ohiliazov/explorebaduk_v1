from sgftree.board import Location, Board

from explorebaduk.constants import Ruleset


def count_japanese(board: Board) -> dict:
    return {Location.BLACK: 0, Location.WHITE: 0}


def count_chinese(board: Board) -> dict:
    return {Location.BLACK: 0, Location.WHITE: 0}


def count_ing(board: Board) -> dict:
    return {Location.BLACK: 0, Location.WHITE: 0}


def count_aga(board: Board) -> dict:
    return {Location.BLACK: 0, Location.WHITE: 0}


def count_new_zealand(board: Board) -> dict:
    return {Location.BLACK: 0, Location.WHITE: 0}


counter_map = {
    Ruleset.JAPANESE: count_japanese,
    Ruleset.CHINESE: count_chinese,
    Ruleset.ING: count_ing,
    Ruleset.AGA: count_aga,
    Ruleset.NEW_ZEALAND: count_new_zealand,
}


def count_score(rules: Ruleset, board: Board) -> dict:
    counter_func = counter_map[rules]
    return counter_func(board)
