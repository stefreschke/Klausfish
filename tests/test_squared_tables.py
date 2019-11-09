"""
Test everything regarding the piece squared tables in piece_squared_tables.py.
"""
import unittest
import chess
import piece_squared_tables as pst
import test_baseclass

PIECE_NAMES = ["n", "k", "q", "b", "r", "p"]


class PieceSquaredTablesTest(test_baseclass.ChessTest):
    """
    Test class for everything regarding piece squared tables.
    """

    # pylint: disable=missing-docstring

    def test_piece_values(self):
        for piece_name in PIECE_NAMES:
            self.piece_value(piece_char=piece_name)

    def test_piece_from_symbol(self):
        self.assertTrue(chess.Piece.from_symbol("R").color)
        self.assertFalse(chess.Piece.from_symbol("r").color)

    def piece_value(self, piece_char):
        piece = chess.Piece.from_symbol(str.lower(piece_char))
        opposite = chess.Piece.from_symbol(str.upper(piece_char))
        self.logger.debug("Piece %s againt %s", piece, opposite)
        self.assertEqual(pst.value(piece, chess.A1), -pst.value(opposite, chess.A8))
        self.assertEqual(pst.value(piece, chess.B1), -pst.value(opposite, chess.B8))
        self.assertEqual(pst.value(piece, chess.A2), -pst.value(opposite, chess.A7))
        self.assertEqual(pst.value(piece, chess.B2), -pst.value(opposite, chess.B7))
        self.assertEqual(pst.value(piece, chess.H1), -pst.value(opposite, chess.H8))
        self.assertEqual(pst.value(piece, chess.G1), -pst.value(opposite, chess.G8))
        self.assertEqual(pst.value(piece, chess.H2), -pst.value(opposite, chess.H7))
        self.assertEqual(pst.value(piece, chess.G2), -pst.value(opposite, chess.G7))


if __name__ == '__main__':
    unittest.main()
