"""
File used to write all kinds of evaluation functions (taking a state as an instance of chess.Board
and returning a number) used for heuristic evaluation functions used in evaluation.py.
"""
import numpy as np
import chess
import piece_squared_tables as pst
import environment


SIMPLE_MATERIAL_VALUES = {  # simple material values as learned by every chess player
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 20
}

STOCKFISH_MATERIAL_VALUES = {
    chess.PAWN: 198,
    chess.KNIGHT: 817,
    chess.BISHOP: 836,
    chess.ROOK: 1270,
    chess.QUEEN: 2521,
    chess.KING: 20000
}

STOCKFISH_MATERIAL_VALUES_ENDGAME = {
    chess.PAWN: 258,
    chess.KNIGHT: 846,
    chess.BISHOP: 857,
    chess.ROOK: 1278,
    chess.QUEEN: 2558,
    chess.KING: 20000
}

SQUARE_VALUES = [1, 1, 1, 1, 1, 1, 1, 1,
                 1, 2, 2, 2, 2, 2, 2, 1,
                 1, 2, 3, 3, 3, 3, 2, 1,
                 1, 2, 3, 4, 4, 3, 2, 1,
                 1, 2, 3, 4, 4, 3, 2, 1,
                 1, 2, 3, 3, 3, 3, 2, 1,
                 1, 2, 2, 2, 2, 2, 2, 1,
                 1, 1, 1, 1, 1, 1, 1, 1]  # used to state the importance of the squares
FILES = [[i * 8 + j for i in range(8)] for j in range(8)]  # list of lists with squares for files
NEIGHBOURING_FILES = [[1]] + [[i + 1, i - 1] for i in range(1, 7)] + [[6]]
    # files that are next to each other


# 61.6 µs ± 533 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
def material_heuristic_slow(state, values=SIMPLE_MATERIAL_VALUES):
    # pylint: disable=dangerous-default-value
    """
    Eine einfache Materialheuristik. Zählt die Figuren auf dem Brett und summiert Materialwerte auf.
    Bei ausgeglichenem Material ist diese Summe 0.

    :param state: Eine beliebige Stellung.
    :param values: Materialwerte für die einzelnen Figuren.
    :return: Integer, Bewertung für die Stellung.
    """
    pieces = state.piece_map().values()
    return np.sum([values[piece.piece_type] if piece.color else -values[piece.piece_type]
                   for piece in pieces])


# 39.3 µs ± 524 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
def material_heuristic_fast(state, values=SIMPLE_MATERIAL_VALUES):
    # pylint: disable=dangerous-default-value
    """
    Eine einfache Materialheuristik. Zählt die Figuren auf dem Brett und summiert Materialwerte auf.
    Bei ausgeglichenem Material ist diese Summe 0.

    :param state: Eine beliebige Stellung.
    :param values: Materialwerte für die einzelnen Figuren.
    :return: Integer, Bewertung für die Stellung.
    """
    pieces = state.piece_map().values()
    result = 0
    for piece in pieces:
        if piece.color:
            result += values[piece.piece_type]
        else:
            result -= values[piece.piece_type]
    return result


def piece_squared_tables(state, value_function=pst.value):
    """
    Piece Squared Table function.

    :param state: The position to look at (instance of chess.Board).
    :param value_function:
        Function that returns a PSQ-value for a given piece and square.
        Python-Chess library objects need to be used accordingly.
    :return:
        Evaluation of a position based on a provided PSQ-function.
    """
    pieces = dict(state.piece_map())
    result = 0
    game_stage = environment.calculate_game_state(state)
    for square, piece in pieces.items():
        result += value_function(piece=piece, square=square, game_stage=game_stage)
    return result


# 87.1 µs ± 60.6 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
def pawn_dictionaries(state):
    """
    Processing the piece_map into two dictionaries (one for each player) that only include pawns.
    This makes analyzing pawn structures much more comfortable.

    :param state: an instance of chess.Board representing the current state
    :return:
        Two dictionaries with lists as values. The keys are the files on the board.
        Note that if a file that does not include pawns of the given side is called,
        a KeyError results.
    """
    white_pawns = {}
    black_pawns = {}
    for square, piece in state.piece_map().items():
        if piece.piece_type == chess.PAWN:
            file_number = chess.square_file(square)
            rank_number = chess.square_rank(square)
            if piece.color:
                pawn_dictionaries_append_rank(white_pawns, file_number, rank_number)
            else:
                pawn_dictionaries_append_rank(black_pawns, file_number, rank_number)
    return white_pawns, black_pawns


def pawn_dictionaries_append_rank(pawn_dictionary, file_number, rank_number):
    """
    Helping function for pawn_dictionaries. Used to reduce code duplication.
    Takes a rank and file number and appends rank number to the list associated to the file number
    in the given pawn dictionary. If that key is invalid an empty list is created before adding the
    rank number.

    :param pawn_dictionary: Dictionary with list values that is supposed to become the pawn dict.
    :param file_number: File the dictionary is supposed to be filled it.
    :param rank_number: The rank the entry to the file should be added to.
    :return:
    """
    try:
        pawn_dictionary[file_number].append(rank_number)
    except KeyError:
        pawn_dictionary[file_number] = [rank_number]


# 51.5 µs ± 539 ns per loop (mean ± std. dev. of 7 runs, 10000 loops each)
def pawn_structure(state):
    """
    Function used for
        1. creating the pawn dictionaries
        2. calling a buuuuunch of functions that need the created dicts
        3. sum their results up to a single number

    :param state: an instance of chess.Board representing the current position
    :return: A whole number
    """
    white_pawns, black_pawns = pawn_dictionaries(state)
    result = 0
    result += doubled_pawns(white_pawns, black_pawns)
    result += isolated_pawns(white_pawns, black_pawns)
    result += passed_pawns(white_pawns, black_pawns)
    return result


def doubled_pawns(white_pawns, black_pawns):
    """
    Function for counting doubled (trippled, quadrupled...) pawns based on two pawn dictionaries.
    Returns whole numbers in any case.
        n means: n doubled pawns for black
        -n means: n doubled pawns for white
    Trippled and quadrupled pawns are counted as three times as bad as doubled pawns.
    Famous saying: "

    :param white_pawns: Dictionary for existing white pawns (keys = files)
    :param black_pawns: Dictionary for existing black pawns (keys = files)
    :return:
    """
    return doubled_pawns_from_pawn_dict(black_pawns) - doubled_pawns_from_pawn_dict(white_pawns)


def doubled_pawns_from_pawn_dict(pawn_dict):
    """
    Helper method for doubled_pawns using a single pawn dictionary. Does not care if pawns are
    black or white. Returns integers >= 0.

    :param pawn_dict: Dictionary (Integer -> [Integer]) built by pawn_dictionaries (keys = files)
    :return: positive value for doubled/tripled pawn score
    """
    result = 0
    for _, pawns in pawn_dict.items():
        if len(pawns) == 2:
            result += 1
        elif len(pawns) > 2:
            result += 3
    return result


def isolated_pawns(white_pawns, black_pawns):
    """
    Method for getting a isolated pawn score based on two pawn dictionaries.
    Returns whole numbers in any case.
        n means: n isolated pawns for black
        -n means: n isolated pawns for white

    :param white_pawns: Dictionary for existing white pawns (keys = files)
    :param black_pawns: Dictionary for existing black pawns (keys = files)
    :return:
        positive value if black has more isolated pawns than white
        negative value if white has more isolated pawns than black
        zero if both sides have equal number of isolated pawns
    """
    result = 0
    for file in white_pawns.keys():
        isolated = True
        for neighbour_file in NEIGHBOURING_FILES[file]:
            try:
                _ = white_pawns[neighbour_file]
                isolated = False
                break
            except KeyError:
                pass
        if isolated:
            result -= len(white_pawns[file])
    for file in black_pawns.keys():
        isolated = True
        for neighbour_file in NEIGHBOURING_FILES[file]:
            try:
                _ = black_pawns[neighbour_file]
                isolated = False
                break
            except KeyError:
                pass
        if isolated:
            result += len(black_pawns[file])
    return result


def passed_pawns(white_pawns, black_pawns):
    """
    Method for getting a passed pawn score based on two pawn dictionaries.
    Returns whole numbers in any case.
        n means: n passed pawns for white
        -n means: n passed pawns for black

    :param white_pawns: Dictionary for existing white pawns (keys = files)
    :param black_pawns: Dictionary for existing black pawns (keys = files)
    :return:
        positive value if white has more passed pawns than black
        negative value if black has more passed pawns than white
        zero if both sides have equal number of passed pawns
    """
    result = 0
    for file, pawns in white_pawns.items():
        highest_pawn = max(pawns)
        passed = True
        for neighbour_file in NEIGHBOURING_FILES[file] + [file]:
            try:
                candidates = black_pawns[neighbour_file]
                if max(candidates) > highest_pawn:
                    passed = False
                    break
            except KeyError:
                pass
        if passed:
            result += 1
    for file, pawns in black_pawns.items():
        lowest_pawn = min(pawns)
        passed = True
        for neighbour_file in NEIGHBOURING_FILES[file] + [file]:
            try:
                candidates = white_pawns[neighbour_file]
                if min(candidates) < lowest_pawn:
                    passed = False
                    break
            except KeyError:
                pass
        if passed:
            result -= 1
    return result


# 100 µs ± 37.3 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
def space_controlled(state):
    """
    Kind of simple evaluation based on the space behind pieces.
    Note that e.g. outposts on the same file cancel each other out accordingly.

    :param state: the current state as an instance of chess.Board
    :return: basically a number of "behind" squares that supposedly are controlled by the players
    """
    result = 0
    for file in FILES:
        highest_white = 0
        lowest_black = 7
        for index, value in enumerate(file):
            square = value
            try:
                if state.piece_at(square).color:
                    highest_white = max(index, highest_white)
                else:
                    lowest_black = min(index, lowest_black)
            except AttributeError:
                pass
        result -= 7 - lowest_black
        result += highest_white
    return result


# 661 µs ± 14.3 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
def piece_safety(board):
    """
    Heuristic trying to assess the safety of pieces. Looks at each piece on the board, gets a list
    of attacking and defending pieces, decides whether or not the piece is safe. Quite costly and
    slow, but could be interesting to see whether or not this feature (that is usually worked out by
    searching deeper) can be of any use done oftly.

    :param board: the current state, oh wonder
    :return: A value summerizing the safety of pieces
        Note: Pieces near the center of the board are considered more important
    """
    result = 0
    for state, occupation in board.piece_map().items():
        square = chess.Square(state)
        white_watchers = [SIMPLE_MATERIAL_VALUES[board.piece_at(sq).piece_type]
                          for sq in board.attackers(color=chess.WHITE, square=square)]
        black_watchers = [SIMPLE_MATERIAL_VALUES[board.piece_at(sq).piece_type]
                          for sq in board.attackers(color=chess.BLACK, square=square)]
        try:
            decision = score_single_square(chess.WHITE,
                                           SIMPLE_MATERIAL_VALUES[occupation.piece_type],
                                           attackers=black_watchers, defenders=white_watchers)\
                if occupation.color else score_single_square(chess.BLACK,
                                                             SIMPLE_MATERIAL_VALUES[
                                                                 occupation.piece_type],
                                                             attackers=white_watchers,
                                                             defenders=black_watchers)
            factor = 1 if decision == chess.WHITE else -1
            result += factor * SQUARE_VALUES[square]
        except AttributeError:
            pass
    return result


def score_single_square(color, piece_value_on, attackers, defenders):
    """
    Helping method for piece_safety. Used to determine whether a square is controlled by white or
    black based on attackers and defenders. Used to determine if a piece is likely lost in the near
    future. Search should make that obvious as well.

    :param color: boolean, The color of the piece that is controlling the square
    :param piece_value_on: the value of the piece occupying the square
    :param attackers:
        A list of pieces (better piece values)
        that attack the piece occupying the square
    :param defenders: A list of pieces (better piece values)
        that defend the piece occupying the square
    :return: boolean, The color that most likely controls the square based on that
    """
    min_attacker = min(attackers) if attackers else None  # if attackers is not empty
    min_defender = min(defenders) if defenders else None  # if defenders is not empty
    if min_attacker is None:
        # piece is not attacked ... ezpz
        return color
    if min_defender is None or piece_value_on > min_attacker:
        # piece is not defended and attacked ... rip
        return not color
    if min_defender < min_attacker:
        # check if square is protected with lower piece value
        # would mean, that the protection is sufficient despite number of attackers
        return color
    if len(attackers) > len(defenders):
        # square seems to be attacked more than defended
        return not color
    # otherwise square probably belongs to player
    return color


def available_moves(state):
    """
    Give some points for having a great selection of moves.
    Goal: Penalize Zugzwang situations!

    :param state: Instance of chess.Board
    :return:
        + number of moves | white moves
        - number of moves | black moves
    """
    factor = 1 if state.turn else -1
    return factor * len(list(state.legal_moves))
