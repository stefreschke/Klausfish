"""
All tests regarding opening and end game look-up.
"""
import unittest
import chess
import test_baseclass
from catalogue import get_catalogue_moves, endgame_lookup, get_endgame_wdl


class CatalogueTests(test_baseclass.ChessTest):
    """
    Test class used for testing opening and end game look-up.
    """

    # pylint: disable=missing-docstring

    def test_opening(self):
        board = chess.Board()
        moves = get_catalogue_moves(board)
        expectation = "r2q1rk1/4bppp/p2p1n2/np5b/3BP1P1/5N1P/PPB2P2/RN1QR1K1 b - - 0 15"

        while moves:  # len(moves) > 0
            board.push(moves[0])
            moves = get_catalogue_moves(board)

        self.assertEqual(board.fen(), expectation)

    def test_endgame(self):
        board = chess.Board("4k3/8/2n5/8/8/8/8/2K1N3 w - - 0 1")
        self.assertEqual(str(endgame_lookup(board)), "e1f3")

        board = chess.Board("8/6k1/2R5/8/8/2K5/6p1/8 w - - 0 1")
        self.assertEqual(str(endgame_lookup(board)), "c6c7")

        board = chess.Board("8/1P4k1/8/8/8/2K5/7r/8 w - - 1 1")
        self.assertEqual(str(endgame_lookup(board)), "c3b3")

        board = chess.Board("8/6k1/2R5/8/8/2K5/6p1/8 b - - 0 1")
        self.assertEqual(str(endgame_lookup(board)), "g7g8")

        board = chess.Board("5R2/4k3/8/8/5r2/8/6K1/8 b - - 0 1")
        self.assertEqual(str(endgame_lookup(board)), "f4f8")

    def test_endgame_wdl(self):
        board = chess.Board("4k3/8/2n5/8/8/8/8/2K1N3 w - - 0 1")
        self.assertEqual(get_endgame_wdl(board), 0)

        board = chess.Board("8/6k1/2R5/8/8/2K5/6p1/8 w - - 0 1")
        self.assertEqual(get_endgame_wdl(board), -1)

        board = chess.Board("8/1P4k1/8/8/8/2K5/7r/8 w - - 1 1")
        self.assertEqual(get_endgame_wdl(board), 1)

        board = chess.Board("8/6k1/2R5/8/8/2K5/6p1/8 b - - 0 1")
        self.assertEqual(get_endgame_wdl(board), 1)

        board = chess.Board("5R2/4k3/8/8/5r2/8/6K1/8 b - - 0 1")
        self.assertEqual(get_endgame_wdl(board), 1)


if __name__ == '__main__':
    unittest.main()
