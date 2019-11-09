"""
Testing simplified engine interface in engine.py.
"""
import time
import unittest
import chess
import test_baseclass
import engine


class SimpleInterfaceTest(test_baseclass.ChessTest):
    """
    Class used for testing the simplified interface within engine.py.
    This interface is used by the simple jupyter notebook GUI provided.
    """

    # pylint: disable=missing-docstring

    def test_starting_position(self):
        starting_position = engine.start_state()
        self.assertTrue(isinstance(starting_position, chess.Board))
        self.assertEqual(1, starting_position.fullmove_number)

    def test_moving_pieces(self):
        position = engine.start_state()
        position = engine.move(position, "e2e4")
        self.assertEqual(1, position.fullmove_number)
        position = engine.move(position, "e7e5")
        self.assertEqual(2, position.fullmove_number)
        try:
            engine.move(position, "e4e5")
            self.fail("Illegal move was possible")
        except AssertionError:
            pass

    def test_getting_mated(self):
        position = mated_position()
        # self.logger.debug("\n" + str(position))
        self.assertTrue(position.is_game_over())
        self.assertTrue(position.is_checkmate())
        self.assertEqual("0-1", position.result())

    def test_search_at_mate(self):
        position = mated_position()
        move_suggestion, resulting_position = engine.search(position, 2)
        self.assertEqual(position.fen(), resulting_position.fen())
        self.assertIsNone(move_suggestion)

    # @unittest.skip("Needs to be refactored at stage of time_manager")
    def test_search_time_limit(self):
        for seconds_allowed in range(6, 10, 5):
            self.search_time_limit(amount_of_time=seconds_allowed)

    def search_time_limit(self, amount_of_time=5):
        position = engine.start_state()
        for _ in range(20):
            position.push(list(position.legal_moves)[0])
        self.logger.info("Searching for %d seconds", amount_of_time)
        timestamp = time.time()
        _, _ = engine.search(position, seconds=amount_of_time)
        timestamp = time.time() - timestamp
        difference = timestamp - amount_of_time
        self.logger.info("Search took %d seconds", timestamp)
        self.logger.info("Difference is %d seconds", difference)
        self.assertGreaterEqual(.1, difference)  # allow .1s of passed time


def mated_position():
    """
    Get the fasted mate possible as a chess.Board() using engine.py.

    :return: chess.Board that shows a mated position
    """
    position = engine.start_state()
    fast_mate = ["g2g5", "e7e5", "f2f3", "d8h4"]
    for moverinho in fast_mate:
        position = engine.move(position, moverinho)
    return position



if __name__ == '__main__':
    unittest.main()
