"""
File for looking up positions in opening and end game data base. Data base files are in ./data/
directory of this repository.
"""
import random
import warnings
import os
import chess
import chess.polyglot
import chess.gaviota

MAX_GAVIOTA_PIECES = 4


def get_catalogue_moves(board):
    """
    Query polyglot opening book for moves.

    :param board: Position to look up the data base for.
    :return: A list of moves that are included in suggested opening repertoire.
    """
    file_path = os.path.dirname(os.path.realpath(__file__))
    with chess.polyglot.open_reader("{}/data/performance.bin".format(file_path)) as polyglot:
        c_moves = []
        for entry in polyglot.find_all(board):
            c_moves.append(entry.move)
        return c_moves


def get_endgame_dtm(board):
    """
    Gets depth-to-mate property of an end game position. Only does not throw an exeption, if there
    are MAX_GAVIOTA_PIECES or less pieces on the board.

    :param board: Position to look up the database for.
    :return: Number of moves to mate (integer value)
    """
    file_path = os.path.dirname(os.path.realpath(__file__))
    with chess.gaviota.open_tablebase("{}/data/Gaviota".format(file_path)) as gaviota:
        return gaviota.probe_dtm(board)


def get_endgame_wdl(board):
    """
    Gets win-draw-loss property of end game position. Only does not throw an exeption, if there are
    MAX_GAVIOTA_PIECES or less pieces on the board.

    :param board: Position to look up the database for.
    :return:
        1 if white wins
        -1 if black wins
        0 if endgame position is drawn
    """
    file_path = os.path.dirname(os.path.realpath(__file__))
    with chess.gaviota.open_tablebase("{}/data/Gaviota".format(file_path)) as gaviota:
        return gaviota.probe_wdl(board)


def endgame_lookup(board):
    """
    Looks up end game data base of a position. Returns the move supposed to be played in this
    position. If number of pieces on board is greater than MAX_GAVIOTA_PIECES, None is returned.

    :param board: Position to look up.
    :return: Instance of chess.Move with the suggested move
    """
    warnings.warn("not working feature", UserWarning)
    # do not use this method
    # see failing unit test to find out why

    if len(board.piece_map()) > MAX_GAVIOTA_PIECES:
        return None

    legal_moves = list(board.legal_moves)
    best_dtm = float('-inf')
    best_move = legal_moves[0]
    for move in legal_moves:
        new_board = board.copy()
        new_board.push(move)
        dtm = get_endgame_dtm(new_board)
        if dtm > best_dtm:
            best_dtm = dtm
            best_move = move

    return best_move


def opening_lookup(state):
    """
    Uses get_catalogue_moves to query for opening moves. Selects a random move from the returned
    list. As a result this ensures the engine will pick random openings that appear to be named in
    the used opening library.

    :param state: State in the opening to look up.
    :return: Instance of chess.Move if a move could be found, None otherwise
    """
    catalogue_moves = get_catalogue_moves(state)
    if catalogue_moves:  # if catalogue_moves not empty
        return catalogue_moves[random.randint(0, len(catalogue_moves) - 1)]
    return None
