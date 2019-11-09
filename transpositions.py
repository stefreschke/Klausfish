"""
Module for everything related to transpositions. Includes transposition table implementation as
well as a class for transposition table entries. It is advised (but not enforced) to put instances
of TranspositionTableEntry to TranspositionTable, as this way a lasting interface can be ensured.
It also prevents AttributeErrors from popping up when using the TranspositionTable.

To write to TranspositionTable, use the following code:
    >>> from chess import Board
    >>> table = TranspositionTable()
    >>> my_board = chess.Board()
    >>> entry = TranspositionTableEntry()
    >>> entry.score = 0
    >>> entry.depth = 1
    >>> entry.moves = list(my_board.legal_moves)
    >>> table[my_board] = entry  # calls my_board.fen()

To read from the same instance of TranspositionTable, use the following code:
    >>> entry = table[my_board]  # again calls my_board.fen()
"""
import logging
import chess

LOGGER = logging.getLogger("chess_logger")
PV_NODE, CUT_NODE, ALL_NODE = range(3)  # types of nodes


def cut_fen(board):
    """
    Efficiently removing the last 2 components of a fen string.

    :param board: Board to take FEN-String from.
    :return: Reduced FEN-String.
    """
    return " ".join(board.fen().split(" ")[:4])


class TranspositionTable(dict):
    """
    Transposition Table for saving search results.
    Currently based on pyDicts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __getitem__(self, key):
        """
        Get-Request für die Transpositionstabelle.
        Nutzt gleichnamige Methode der Klasse Dictionary.

        :param key: Zustand in fen-Notation!
        :return: Objekt der Klasse TranspositionTableEntry
        """
        return super().__getitem__(cut_fen(key) if isinstance(key, chess.Board) else key)

    def __setitem__(self, key, val):
        """
        Set-Request für die Transpositionstabelle.
        Nutzt gleichnamige Methode der Klasse Dictionary.

        :param key: Zustand in fen-Notation!
        :param val: Objekt der Klasse TranspositionTableEntry
        :return: None
        """
        super().__setitem__(cut_fen(key) if isinstance(key, chess.Board) else key, val)


class TranspositionTableEntry:
    """
    An entry to a TranspositionTable.
    Leaves room for all thinkable entries one in the future might like to add to it...
    Implements comparison protocol based on score attribute.
    """
    def __init__(self, moves=None, depth=0, score=0, node_type=None, **kwargs):
        self.__moves = moves
        self.__depth = depth
        self.__score = score
        self.__node_type = node_type
        if node_type is None:
            self.handle_alpha_beta_kwargs(**kwargs)

    @property
    def moves(self):
        """
        Ordered moves to guide next iteration over this state.
        :return:
        """
        return self.__moves

    @moves.setter
    def moves(self, val):
        """
        Searcher needs to set this property, thats why it's public.
        :param val: builtins.list of sorted moves
        :return:
        """
        self.__moves = val

    @property
    def score(self):
        """
        Score of the past iteration for the next iteration on this state.
        If out of bound, this could provide an additional cut off.
        :return:
        """
        return self.__score

    @score.setter
    def score(self, val):
        """
        Searcher needs to set this property, thats why it's public.
        :param val: number of some sort for a score of a position
        :return:
        """
        self.__score = val

    @property
    def depth(self):
        """
        Depth the current state was searched at (the higher the better).
        Helps future iterations decide if this node was searched good enough.
        :return:
        """
        return self.__depth

    @depth.setter
    def depth(self, val):
        """
        Searcher needs to set this property, thats why it's public.
        :param val: integer value showing the searched depth
        :return:
        """
        self.__depth = val

    @property
    def node_type(self):
        """
        Additional field for node type. According to CPW the node type could be a useful
        information to have. However right now we don't use that information. Thats why there is
        no mention of this in the text.
        :return:
        """
        return self.__node_type

    def fill(self, score, depth, moves):
        """
        Set all possible entries right away.
        :param score: Score to set
        :param depth: Depth to set
        :param moves: Moves (ordered) to set
        :return:
        """
        self.__score = score
        self.__moves = moves
        self.__depth = depth

    def calc_node_type(self, alpha, beta):
        """
        Method used to calculate the node type based on passed alpha and beta values.
        :param alpha: number (alpha value)
        :param beta: number (beta value)
        :return: void
        """
        if self.__score >= beta:
            self.__node_type = CUT_NODE
        elif self.__score <= alpha:
            self.__node_type = ALL_NODE
        else:
            self.__node_type = PV_NODE

    def handle_alpha_beta_kwargs(self, alpha=None, beta=None):
        """
        Calculate node type if alpha and beta are provided.

        :param alpha: number for alpha value
        :param beta: number for beta value
        :return:
        """
        if alpha is not None and beta is not None:
            self.calc_node_type(alpha, beta)

    # Methods for comparing TranspositionTableEntries
    def __lt__(self, other):
        return self.__score < other.score

    def __eq__(self, other):
        return self.__score == other.score


def get_prime_line(state, transposition_table):
    """
    Function that returns the PV as a list of uci-string-moves. Mostly used for either unittesting
    or fancy outputting. As to the current point of implementation, the calculated moves are all
    stored inside the transposition table, looking up the PV needs to be done there.

    :param my_fransposition_table: to look up for PV
    :param state: the lookup at transposition table should start it
        Goal is to find that entry, take its best move, look up for the resulting position of that
        move a.s.o.
    :return: list of moves as simple UCI strings (nothing chess.Move related)
        e.g. ["e5e6", "f7e6", "e1e6"] (centralizing a rook/queen)
    """
    board = state.copy()
    moves = []
    while True:
        try:
            entry = transposition_table[board]
            assert isinstance(entry, TranspositionTableEntry)
            best_move = entry.moves[0]
            moves.append(best_move)
            board.push(best_move)
        except KeyError:
            break
    return moves
