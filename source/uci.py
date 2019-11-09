"""
This file is the UCI implementation for this engine. Uses a message queue to handle all incoming
commands (which were sent through STDIN) and busy waits for something to do.
"""
from threading import Thread
import logging
import queue
import sys
import chess
from chess import Move, Board
from time_management import TimeManager

INITIAL = chess.Board().fen()
LOGGER = logging.getLogger("chess_logger")


def add_input(input_queue):
    """
    Writes something to a given queue from STDIN.

    :param input_queue: Queue to use to handle STDIN.
    :return:
    """
    while True:
        input_queue.put(sys.stdin.readlines(1)[-1][:-1])


def main():
    """
    https://stackoverflow.com/a/19655992
    """

    # pylint: disable=too-many-branches

    input_queue = queue.Queue()
    input_thread = Thread(target=add_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    board = chess.Board(INITIAL)
    time_manager = TimeManager()
    LOGGER.debug("------ NEW SESSION ------")

    while True:
        if not input_queue.empty():
            smove = input_queue.get()
            LOGGER.warning("Command captured: %s", smove)
        else:
            if time_manager.done:
                move_to_go = time_manager.decision
                assert move_to_go is not None
                print('bestmove', move_to_go)
            continue

        if smove == 'quit':
            LOGGER.debug("UCI Quit called, Engine dismissed")
            break

        elif smove == "isready":
            print("readyok")

        elif smove == 'uci':
            print("id name Studienarbeitsengine")
            print("id author Daniel und Stefan")

        elif smove == "ucinewgame":
            board = Board()

        elif smove == "position startpos":
            board = Board()

        elif smove.startswith("position startpos moves"):
            moves = [Move.from_uci(uci=uci) for uci in smove.split(" ")[3:]]
            LOGGER.debug("Setting moves: %s", str(moves))
            board = Board()
            for move in moves:
                board.push(move)

        elif smove.startswith("go"):
            parts = smove.split(" ")[1:]
            LOGGER.debug("Parts of go: %s", parts)
            information = process_uci_time_information(*parts)\
                if len(parts) % 2 == 0 else {"infinite": True}
            time_manager.info_from_uci(**information)
            time_manager.perform_search(board.copy())

        elif smove.startswith("stop"):
            pass

        else:
            print("Error (unkown command):", smove)


# go wtime 1200000 btime 1200000 winc 0 binc 0 movestogo 40
def process_uci_time_information(*args):
    """
    Converting additional parameters of "go" command to dictionary for easier usage.

    :param args: List of parameters and values deriving from "go" call.
    :return: Dictionary with information contained by the parameters.
    """
    LOGGER.debug("Process UCI time specs from following parameter: %s", args)
    keys = args[0::2]
    values = args[1::2]
    assert len(keys) == len(values)
    information = {}
    for i, item in enumerate(keys):
        information[item] = float(values[i])
    return information


def setup_logger():
    """
    Setup console logger in case the UCI is used.
    This method will only be called by the main loop of this file.

    :return: Nothing
    """
    mc_logger = logging.getLogger('chess_logger')
    mc_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('uci.log', "w+")
    # ch = logging.StreamHandler()
    file_handler.setLevel(logging.DEBUG)
    # ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    # ch.setFormatter(formatter)
    mc_logger.addHandler(file_handler)
    # mc_logger.addHandler(ch)


if __name__ == '__main__':
    setup_logger()
    main()
