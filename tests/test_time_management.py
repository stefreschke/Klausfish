"""
File used for testing everything from time_management.py. This mostly referes to the instances of
TimeManager as the Clock is not really interesting.
"""
import unittest
import time
import chess
import test_baseclass
import time_management


class TimeManagerTest(test_baseclass.ChessTest):
    """
    Testing time management and especially TimeManager.
    """

    # pylint: disable=missing-docstring

    def setUp(self):
        super().setUp()
        self.clock = time_management.Clock(base_time=10000)
        self.manager = time_management.TimeManager(time_control=self.clock)

    def test_manager_spending_time(self):
        self.manager.spent_time(6000)
        self.assertEqual(4000, self.manager.time_control.base_time)

    def test_manager_allocating_time(self):
        self.manager.moves_to_go = 10
        allocated_time = self.manager.allocate_time()
        self.assertEqual(self.manager.time_control.base_time / (self.manager.moves_to_go * 1000),
                         allocated_time)

    @unittest.skip("Feature not needed for current focus set")
    def test_hard_time_cut_at_obvious_decision_or_look_up(self):
        starting_position = chess.Board()
        time_start = time.time()
        self.manager.run_searcher_for(seconds=10, on_board=starting_position,
                                      look_up_in_opening=False, look_up_in_end_game=False)
        self.logger.debug("Got move for starting position: %s", self.manager.decision)
        # since we don't really care and the move is looked up immidiately
        self.assertLess(time.time() - time_start, 1)







if __name__ == '__main__':
    unittest.main()
