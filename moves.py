"""
This file contains any effort to sort a list of moves statically. Ideally the most promising moves
should be at the top of this list to make the search as efficiently as possible. This is also done
through the previous iterations and their move suggestions through the transposition table.

However, also sorting moves statically could be interesting. E.g. moves for rest search could be
narrowed down by only selecting taking moves.
"""
import logging
import chess
from heuristics import SIMPLE_MATERIAL_VALUES as VALUES

LOGGER = logging.getLogger("chess_logger")


def recaptures(board):
    """
    Method returning an unordered list of recapturing moves given a board with move stack.
    If move stack is empty, an empty list will be returned.
    Should not throw any Exceptions as IndexError is excepted.

    :param board: an instance of Board with a move stack
    :return: List of moves that are recaptures
    """
    try:
        last_move = board.move_stack[-1]
        target = last_move.to_square
        return [move for move in board.legal_moves if move.to_square == target]
    except IndexError:  # if move stack is empty:
        return []


def mvv_lva(piece, captures):
    """
    MVV - LVA(Most Valuable Victim - Least Valuable Aggressor)
    https: // www.chessprogramming.org / MVV - LVA

    :param piece: e.g. knight
    :param captures: e.g. queen
    :return: e.g. queen + (king - knight)/king
    """
    aggressor, victim = VALUES[piece.piece_type], VALUES[captures.piece_type]
    return victim + (VALUES[chess.KING] - aggressor) / VALUES[chess.KING]


def is_move_check(board, move):
    """
    Checks whether or not a move is checking the opponent.

    :param board: An instance of chess.Board
    :param move: An instance of chess.Move
    :return:
    """
    board.push(move)
    checked = board.is_check()
    board.pop()
    return checked


def is_move_takes(board, move):
    """
    Checks whether or not a move is a "taking" move.

    :param board: An instance of chess.Board
    :param move: An instance of chess.Move
    :return:
        True, if move is e.g. "cxd4"
        False, if move is just a normal move like "e8Q"
    """
    victim = board.piece_at(move.to_square)
    aggressor = board.piece_at(move.from_square)
    if victim is None:
        return False, 0
    return True, mvv_lva(aggressor, victim)


def is_move_recapture(board, move):
    """
    Checks whether a move is a recapture.
    Needs a not empty move stack.

    :param board: An instance of chess.Board
    :param move: An instance of chess.Move
    :return:
    """
    last_move = board.move_stack[-1]
    board.pop()
    if is_move_takes(board, last_move):
        board.push(last_move)
        return move.to_square == last_move.to_square
    return False


def is_move_forward(board, move):
    """
    Checks whether or not a move is a "advancing movement".

    :param board: An instance of chess.Board
    :param move: An instance of chess.Move
    :return:
        True, if move is e.g. "1. d4" or "1. ... d5"
        False, if move is e.g. "2. Nf3g1" or "2. Nf6g8"
    """
    to_square_row = (move.to_square - 1) // 8
    from_square_row = (move.from_square - 1) // 8
    if board.turn:
        return to_square_row > from_square_row
    return from_square_row > to_square_row


def moves_for_rest_search(board):
    """
    Method that removes moves that do not calm the situation from a LegalMoveGenerator.

    :param board: Instance of chess.Board
    :param moves: Instance of chess.LegalMoveGenerator
    :return:
        A List of taking moves.
    """
    number_of_moves = 0
    moves = list(board.legal_moves)
    for move in moves:
        takes, prio = is_move_takes(board, move)
        if takes:
            move.prio = prio
            number_of_moves += 1
        else:
            move.prio = -1
    # LOGGER.debug("%d moves for rest search at %s", number_of_moves, board.fen())
    moves.sort(key=lambda x: x.prio, reverse=True)
    return moves[:number_of_moves]


def best_move_for_rest_search(board):
    """
    Get only one move for rest search.

    :param board: Instance of chess.Board
    :return: Instance of chess.Move
    """
    moves = moves_for_rest_search(board)
    if moves:  # len(moves) > 0
        return moves[0]
    return None


def prioritize_move(board, move):
    """
    Gets a priority value (number) for a given move on a given position (through Board object).
    Return value should corrolate with how promising the move is. More promising moves should give
    higher values than less promising moves.

    :param board: Instance of chess.Board
    :param move: Instance of chess.Move
    :return: Number, priority value
    """
    if is_move_check(board, move):
        return 21
    takes, prio = is_move_takes(board, move)
    if takes:
        return prio
    if is_move_forward(board, move):
        return 1
    return 0


def prioritized(board):
    """
    Generates moves for a position based on the passed Board object.
    Moves are returned as list sorted from most promising to least promising.

    :param board: Instance of chess.Board or something else that implements self.legal_moves
    :return:
        Sorted list of chess.Moves!
        Priority value is assigned as instance value
    """
    moves = list(board.legal_moves)
    for move in moves:
        move.priority = prioritize_move(board, move)
    moves.sort(key=lambda x: x.priority, reverse=True)
    return moves
