"""
File used for testing everything from environment.py. Environment.py got less and less important
with time, thats why this class is very empty right now.
"""
import unittest
import chess
import test_baseclass
import environment

# classical stale mate position
STALE_MATE = "k7/8/1K1B4/8/3N4/8/8/8 b - - 3 2"


class EnvironmentTest(test_baseclass.ChessTest):
    """
    Test all functions from environment.py within this class!
    """
    # pylint: disable=missing-docstring

    def test_utility_drawn_position(self):
        drawn_position = chess.Board(STALE_MATE)
        self.assertTrue(drawn_position.is_game_over())
        self.assertEqual(0, environment.utility(drawn_position))

    def test_turn_white(self):
        starting_position = chess.Board()
        self.assertEqual(chess.WHITE, starting_position.turn)

    def test_turn_black(self):
        starting_position = chess.Board()
        starting_position.push(chess.Move.from_uci("e2e4"))
        self.assertEqual(chess.BLACK, starting_position.turn)

    # pylint: disable=no-self-use
    #  This is a test that does not assert. Accept that @pylint!
    @unittest.skip("Not needed as repetitive test")
    def test_write_file(self):
        # pylint: disable=too-many-function-args
        #  see implementation of Writer
        with environment.Writer("asdf.pgn") as file:
            file.move("e2e4")
