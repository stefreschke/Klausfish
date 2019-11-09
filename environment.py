"""
File used for some really basic functions, including parts of the defined chess game G.
"""
import chess
import chess.pgn


def utility(state):
    """
    Utility function. Returns which site has won at finished game.

    :param state: Probable final state that needs to be checked.
    :return:
        100000 (1000 Centipawns if value["pawn"] == 1) if white wins
        -100000 if black wins
        0 if game is drawn or not yet finished
    """
    res = state.result()
    if res == "1-0":
        return 100000
    if res == "0-1":
        return -100000
    return 0


# Game states
OPENING, MIDDLE_GAME, END_GAME = range(3)


def calculate_game_state(state):
    """
    Calculates the current game state. Uses number of pieces and full move number to check for
    OPENING, with less than 12 pieces it presumes the END_GAME. Defaults to MIDDLE_GAME.

    :param state: State to calculate game state of.
    :return: Gamestate (one of environment.OPENING, -MIDDLE_GAME, -END_GAME
    """
    number_of_pieces = len(state.piece_map())
    if state.fullmove_number < 10 and number_of_pieces > 14:
        return OPENING
    if number_of_pieces < 12:
        return END_GAME
    return MIDDLE_GAME


class Writer:
    """
    Class used to write a PGN while playing a game.
    """
    def __init__(self, filename, **kwargs):
        self.__pgn_game = chess.pgn.Game()
        self.__pgn = self.__pgn_game
        self.__filename = filename
        self.__parse_header_kwargs(**kwargs)

    def __parse_header_kwargs(self, site="", event="", white="", black="", round_number="",
                              date=""):
        # pylint: disable=too-many-arguments
        #   This is a method to get as many kwargs as possible.
        #   Therefore there is no reason to limit the number of arguments.
        self.__pgn_game.headers["Site"] = site if site != "" else self.__filename
        self.__pgn_game.headers["Event"] = event
        self.__pgn_game.headers["White"] = white
        self.__pgn_game.headers["Black"] = black
        self.__pgn_game.headers["Round"] = round_number
        self.__pgn_game.headers["Date"] = date

    def save(self):
        """
        Write the PGN to specified file
        :return:
        """
        with open(self.__filename, "w", encoding="utf-8") as new_pgn:
            new_pgn.write(self.__pgn_game.__str__())

    def move(self, move):
        """
        Write a single move to PGN file.
        :param move:
        :return:
        """
        if isinstance(move, chess.Move):
            self.__pgn = self.__pgn.add_variation(move)
        elif isinstance(move, str):
            self.__pgn = self.__pgn.add_variation(chess.Move.from_uci(move))
        else:
            raise ValueError("Need to provide move as uci-string or chess.Move, got " + str(move))

    def __enter__(self):
        """
        Do nothing, just implement enter-exit protocol to allow with statement use.
        :return:
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Save PGN file after with statement termination.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.save()
