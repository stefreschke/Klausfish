"""
Test everything from transpositions.py.
Includes classes TranspositionTable and TranspositionTableEntry.
"""
import unittest
from random import randint
import chess
import test_baseclass
import transpositions


class TranspositionTableTest(test_baseclass.ChessTest):
    """
    Testing stuff related to TranspositionTable.
    Also tests TranspositionTableEntry features, because those classes share a connection that would
    render all kinds of additional test classes pointless.
    """
    def setUp(self):
        super().setUp()
        self.transposition_table = transpositions.TranspositionTable(max_size=10)

    @unittest.skip("Not needed, feature was removed")
    def test_replace(self):
        """
        Testing deleting old entries in favor of new ones.
        Not needed currently, because that feature was removed from the engine.
        :return:
        """
        boards = get_a_bunch_of_sample_boards()
        selected_list = boards[:10]
        for board in selected_list:
            score = randint(1, 10)
            depth = randint(1, 10)
            board.assigned_score = score
            board.assigned_depth = depth
            self.transposition_table[board] = transpositions.TranspositionTableEntry(score=score,
                                                                                     depth=depth)
        new_one = boards[12]
        self.transposition_table[new_one] = transpositions.TranspositionTableEntry(score=11,
                                                                                   depth=11)
        try:
            _ = self.transposition_table[selected_list[0]]
            self.fail("The presumed entry was not deleted.")
        except KeyError:
            pass

    def test_table_entry_node_type(self):
        """
        Test node_type(s) on TranspositionTableEntry.
        Should sort PV, ALL and CUT nodes accordingly.
        :return:
        """
        entry = transpositions.TranspositionTableEntry(score=0, alpha=-1, beta=1)
        self.assertEqual(transpositions.PV_NODE, entry.node_type)
        entry.score = -1
        entry.calc_node_type(-1, 1)
        self.assertEqual(transpositions.ALL_NODE, entry.node_type)
        entry.score = 1
        entry.calc_node_type(-1, 1)
        self.assertEqual(transpositions.CUT_NODE, entry.node_type)

    def test_fill(self):
        """
        Test method used to fill all instance attributes of TranspositionTableEntry at once.
        :return:
        """
        entry = transpositions.TranspositionTableEntry()
        entry.fill(score=4, depth=5, moves=[1, 2, 3])

        self.assertEqual(entry.score, 4)
        self.assertEqual(entry.depth, 5)
        self.assertEqual(entry.moves, [1, 2, 3])


def get_a_bunch_of_sample_boards():
    """
    Just return a number of chess.Boards.
    Creates one for each possible first move.
    :return:
    """
    board = chess.Board()
    boards = []
    for move in board.legal_moves:
        copy = board.copy()
        # pylint: disable=no-member
        #   chess.BaseBoard may have no push member, but this is a chess.Board!
        copy.push(move)
        boards.append(copy)
    return boards


if __name__ == '__main__':
    unittest.main()
