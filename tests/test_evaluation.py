"""
Testing everything within evaluation.py.
Therefore the whole handling of LinearEvaluation is the prime purpose of this test.
"""
import unittest
import chess
import test_baseclass
import evaluation
from heuristics import material_heuristic_fast, piece_squared_tables


class LinearEvaluationTests(test_baseclass.ChessTest):
    """
    Testing LinearEvaluation from evaluation.py.
    """

    # pylint: disable=missing-docstring

    def setUp(self):
        super().setUp()
        self.evaluation = evaluation.LinearEvaluation()

    def tearDown(self):
        super().tearDown()
        del self.evaluation

    def test_feature_list(self):
        empty_board = chess.Board()
        empty_board.empty()
        self.assertEqual(0, self.evaluation.calculate(empty_board))

        self.evaluation.add_feature(feature=lambda _: 1, weight=1)
        self.assertEqual(1, self.evaluation.calculate(empty_board))
        self.evaluation.add_feature(feature=lambda _: 3, weight=1)
        self.assertEqual(4, self.evaluation.calculate(empty_board))
        self.evaluation.add_feature(feature=lambda _: 5, weight=1)
        self.assertEqual(9, self.evaluation.calculate(empty_board))

        self.evaluation.remove_feature(2)
        self.assertEqual(4, self.evaluation.calculate(empty_board))
        self.evaluation.remove_feature(1)
        self.assertEqual(1, self.evaluation.calculate(empty_board))
        self.evaluation.remove_feature(0)
        self.assertEqual(0, self.evaluation.calculate(empty_board))

    def test_actually_good_features(self):
        board = chess.Board()
        dummy_evaluation = material_heuristic_fast(board) + piece_squared_tables(board)
        self.evaluation.add_feature(feature=material_heuristic_fast, weight=1)
        self.evaluation.add_feature(feature=piece_squared_tables, weight=1)
        self.assertEqual(dummy_evaluation, self.evaluation.calculate(state=board))

    def test_protocol(self):
        board = chess.Board()
        self.evaluation.add_feature(feature=material_heuristic_fast, weight=1)
        expected_result = self.evaluation.calculate(state=board)
        self.assertEqual(expected_result, self.evaluation[board])

    def test_simplified_eval(self):
        simplified_eval = evaluation.SimplifiedEvaluationFunction()
        board = chess.Board()
        with_rook = simplified_eval[board]
        board.remove_piece_at(chess.A1)
        without_rook = simplified_eval[board]
        board.push(chess.Move.from_uci("e2e4"))
        with_advanced_pawn = simplified_eval[board]
        self.assertEqual(0, with_rook)
        self.assertEqual(-500, without_rook)
        self.assertGreater(with_advanced_pawn, without_rook)


if __name__ == '__main__':
    unittest.main()
