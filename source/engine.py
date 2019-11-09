"""
Simple interface for non UCI interaction.

Provides interface that can be used like:
    >>> from engine import *
    >>> s = start_state()
    >>> s = move(s, "e2e4")
    >>> _, s = search(s, 10)  # searching for 10s
"""
import logging
import chess
import chess.pgn
import time_management


LOGGER = logging.getLogger("chess_logger")


def start_state():
    """
    Create start state s_0 by creating an instance of chess.Board without parameters.
    :return: start state s_0 as chess.Board
    """
    return chess.Board()


def move(state=None, actual_move=None):
    """
    Take a uci-move-string and push the move on the given board.
    Copies the given instance of chess.Board to ensure call-by-value-ish behaviour.

    :param state: instance of chess.Board
    :param actual_move: string containing uci move (e.g. "e2e4", "d7d8"; not "e4", "d8Q+" or so)
    :return: copied state with the move pushed
    """
    copy = state.copy()
    copy.push(chess.Move.from_uci(uci=actual_move))
    return copy


def search(state=None, seconds=60, opening_look_up=True, end_game_look_up=False):
    """
    Let the engine think of a move to push to the given state.

    :param state: instance of chess.Board
    :param seconds: number of seconds the engine should think about its move
    :param opening_look_up: whether opening look up is allowed.
    :param end_game_look_up: whether end game look up is allowed.
    :return:
        instance of chess.Move with the engines decision,
        instance of chess.Board with the pushed move (see move)
    """
    assert isinstance(state, chess.Board)
    if state.is_game_over():
        return None, state
    manager = time_management.TimeManager(time_control=time_management.Clock(base_time=seconds))
    manager.allocate_time = lambda: seconds
    search_copy = state.copy()
    manager.perform_search(board=search_copy,
                           look_up_in_opening=opening_look_up,
                           look_up_in_end_game=end_game_look_up)
    copy = state.copy()
    copy.push(manager.decision)
    return manager.decision, copy


def setup_logger():
    """
    Setup logging. Not necessary for interface.
    :return:
    """
    mc_logger = logging.getLogger('chess_logger')
    mc_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    mc_logger.addHandler(console_handler)


if __name__ == '__main__':
    setup_logger()
