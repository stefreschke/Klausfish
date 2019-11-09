"""
Unittests for everything regarding the static order of moves.
Usually everything of that is written to moves.py.
"""
import unittest
import chess
import moves
import test_baseclass
from heuristics import SIMPLE_MATERIAL_VALUES

FEN_WHITE = "2k5/pppppppp/8/3N4/3n4/8/PPPPPPPP/2K5 w - - 0 1"
FEN_BLACK = "2k5/pppppppp/8/3N4/3n4/8/PPPPPPPP/2K5 b - - 0 1"


class SortingMovesTest(test_baseclass.ChessTest):
    """
    Testing everything thats sorting moves.
    """

    # pylint: disable=missing-docstring

    def setUp(self):
        super().setUp()
        self.board_white = chess.Board(FEN_WHITE)
        self.board_black = chess.Board(FEN_BLACK)

    def tearDown(self):
        super().tearDown()
        del self.board_black
        del self.board_white

    def test_attacking_moves(self):
        board = chess.Board("r1bqkb1r/pppp1ppp/2nn4/1B2N3/8/8/PPPP1PPP/RNBQR1K1 b kq - 0 6")
        all_moves = board.legal_moves
        selected_moves = moves.moves_for_rest_search(board=board)
        self.assertLess(len(selected_moves), len(list(all_moves)))
        self.assertIn(chess.Move.from_uci("d6b5"), selected_moves)
        self.assertIn(chess.Move.from_uci("c6e5"), selected_moves)
        self.assertEqual(len(selected_moves), 2)

    def test_checking_moves(self):
        checking_moves = [chess.Move.from_uci("d5e7"), chess.Move.from_uci("d5b6")]
        not_checking_moves = [chess.Move.from_uci("d5e3"), chess.Move.from_uci("d5f4")]
        for move in checking_moves:
            self.assertTrue(moves.is_move_check(self.board_white, move))
        for move in not_checking_moves:
            self.assertFalse(moves.is_move_check(self.board_white, move))

    def test_taking_moves(self):
        taking_moves = [chess.Move.from_uci("d5e7"), chess.Move.from_uci("d5c7")]
        not_taking_moves = [chess.Move.from_uci("d5f6"), chess.Move.from_uci("d5b6")]
        for move in taking_moves:
            takes, _ = moves.is_move_takes(self.board_white, move)
            self.assertTrue(takes)
        for move in not_taking_moves:
            takes, _ = moves.is_move_takes(self.board_white, move)
            self.assertFalse(takes)

    def test_forward_moves_white(self):
        forward_moves = [chess.Move.from_uci("d5b6"), chess.Move.from_uci("d5c7"),
                         chess.Move.from_uci("d5e7"), chess.Move.from_uci("d5f6")]
        backward_moves = [chess.Move.from_uci("d5b4"), chess.Move.from_uci("d5c3"),
                          chess.Move.from_uci("d5e3"), chess.Move.from_uci("d5f4")]
        for move in forward_moves:
            self.assertTrue(moves.is_move_forward(self.board_white, move))
        for move in backward_moves:
            self.assertFalse(moves.is_move_forward(self.board_white, move))

    def test_forward_moves_black(self):
        forward_moves = [chess.Move.from_uci("d5b3"), chess.Move.from_uci("d5c2"),
                         chess.Move.from_uci("d5e2"), chess.Move.from_uci("d5f3")]
        backward_moves = [chess.Move.from_uci("d5b5"), chess.Move.from_uci("d5c6"),
                          chess.Move.from_uci("d5e6"), chess.Move.from_uci("d5f5")]
        for move in forward_moves:
            self.assertTrue(moves.is_move_forward(self.board_black, move))
        for move in backward_moves:
            self.assertFalse(moves.is_move_forward(self.board_black, move))

    def test_prioritized_moves(self):
        all_moves = moves.prioritized(self.board_white)
        priorities = [x.priority for x in all_moves]
        sorted_prios = priorities.copy()
        sorted_prios.sort(reverse=True)
        self.assertEqual(sorted_prios, priorities)

    def test_mvv_lva(self):
        taking_moves = [chess.Move.from_uci("d5e7"), chess.Move.from_uci("d5c7")]
        for move in taking_moves:
            _, prio = moves.is_move_takes(self.board_white, move)
            expected = SIMPLE_MATERIAL_VALUES[chess.PAWN] + \
                       (SIMPLE_MATERIAL_VALUES[chess.KING] - SIMPLE_MATERIAL_VALUES[chess.KNIGHT])\
                       / SIMPLE_MATERIAL_VALUES[chess.KING]
            self.assertEqual(expected, prio)

    def test_rest_search_moves(self):
        white_rest_moves = moves.moves_for_rest_search(board=self.board_white)
        black_rest_moves = moves.moves_for_rest_search(board=self.board_black)
        self.logger.debug("rest_moves %s normal_moves %s", len(white_rest_moves),
                          len(list(self.board_white.legal_moves)))
        self.logger.debug("rest_moves %s normal_moves %s", len(black_rest_moves),
                          len(list(self.board_black.legal_moves)))
        self.assertLess(len(white_rest_moves), len(list(self.board_white.legal_moves)))
        self.assertLess(len(black_rest_moves), len(list(self.board_black.legal_moves)))


if __name__ == '__main__':
    unittest.main()
