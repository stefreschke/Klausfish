"""
This file is used to test everything written in heuristics.py.
Also tests piece squared tables.
"""
import unittest
import chess
import heuristics
import test_baseclass


class HeuristicTests(test_baseclass.ChessTest):
    """
    Class used to test every bit of stuff used in heuristics.py.
    Also tests piece squared tables as those, as stated in heuristics.py, would actually belong
    there. However, the numpy arrays take up a lot of space and are horrible to look at.
    """

    # pylint: disable=missing-docstring

    def test_material_heuristic(self, state=chess.Board(), expectation=0):
        self.assertEqual(expectation, heuristics.material_heuristic_fast(
            state=state, values=heuristics.SIMPLE_MATERIAL_VALUES))

    def test_material_heuristic_with_values(self):
        positions = {
            "8/2k5/3b4/8/2q5/8/8/3QK3 b - - 0 1": -3,
            "6k1/R7/8/5p2/8/8/Rr4r1/5K2 w - - 0 1": -1
        }
        for fen, evaluation in positions.items():
            state = chess.Board(fen=fen)
            self.test_material_heuristic(state=state, expectation=evaluation)

    def test_piece_squared_tables_opening(self):
        board = chess.Board()
        pst_value = heuristics.piece_squared_tables(board)
        board.push(chess.Move.from_uci("e2e4"))
        new_value = heuristics.piece_squared_tables(board)
        board.push(chess.Move.from_uci("e7e5"))

        self.assertEqual(0, pst_value)
        self.assertGreater(new_value, pst_value)
        self.assertEqual(pst_value, heuristics.piece_squared_tables(board))

    def test_piece_squared_tables_error_assertions(self):
        try:
            heuristics.piece_squared_tables(state=chess.Board(), value_function=lambda x, y: 0)
            self.fail("PSQ does not fail with given function "
                      "that does not contain request kw-arguments!")
        except TypeError:
            pass

    def test_space_controlled(self):
        board = chess.Board()
        self.assertEqual(0, heuristics.space_controlled(board))
        board.push(chess.Move.from_uci("e2e4"))
        self.assertEqual(2, heuristics.space_controlled(board))

    def test_neighbouring_files(self):
        self.assertEqual([1], sorted(heuristics.NEIGHBOURING_FILES[0]))
        self.assertEqual([0, 2], sorted(heuristics.NEIGHBOURING_FILES[1]))
        self.assertEqual([1, 3], sorted(heuristics.NEIGHBOURING_FILES[2]))
        self.assertEqual([2, 4], sorted(heuristics.NEIGHBOURING_FILES[3]))
        self.assertEqual([3, 5], sorted(heuristics.NEIGHBOURING_FILES[4]))
        self.assertEqual([4, 6], sorted(heuristics.NEIGHBOURING_FILES[5]))
        self.assertEqual([5, 7], sorted(heuristics.NEIGHBOURING_FILES[6]))
        self.assertEqual([6], sorted(heuristics.NEIGHBOURING_FILES[7]))

    def test_pawn_structure_doubled(self):
        board = chess.Board("1k6/8/p1p1p2p/1p1p1p2/8/P1P1P1P1/P1P4P/3K4 w - - 0 1")
        white, black = heuristics.pawn_dictionaries(board)
        doubled_pawn_value = heuristics.doubled_pawns(white, black)
        self.assertEqual(-2, doubled_pawn_value)

    def test_pawn_structure_isolated(self):
        board = chess.Board("1k6/8/p1p1p2p/1p1p1p2/8/P1P1P1P1/P1P4P/3K4 w - - 0 1")
        white, black = heuristics.pawn_dictionaries(board)
        isolated_pawn_values = heuristics.isolated_pawns(white, black)
        self.assertEqual(-4, isolated_pawn_values)

    def test_pawn_structure_passed(self):
        positions = [(None, 0),
                     ("1k6/8/3pp3/p1p1P1pP/2Pp4/6P1/Pp6/1K6 w - - 0 1", -1)]
        for fen, expected in positions:
            board = chess.Board(fen) if isinstance(fen, str) else chess.Board()
            white, black = heuristics.pawn_dictionaries(board)
            self.logger.info("weiße Bauern: %s", white)
            self.logger.info("schwarze Bauern: %s", black)
            self.assertEqual(expected, heuristics.passed_pawns(white, black))

    def test_square_values(self):
        vals = heuristics.SQUARE_VALUES
        self.assertEqual(4, vals[int(chess.E4)])
        self.assertEqual(3, vals[int(chess.C3)])
        self.assertEqual(2, vals[int(chess.F7)])
        self.assertEqual(1, vals[int(chess.H8)])


if __name__ == '__main__':
    unittest.main()
