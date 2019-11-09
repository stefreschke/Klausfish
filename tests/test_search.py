"""
Unittests for everything related to searching.py.
Is the main test file used to test the engines ability to search the tree.
"""
import time
import unittest
import chess
import pandas as pd
import transpositions
import test_baseclass
from searching import Search


class SearchTests(test_baseclass.ChessTest):
    """
    Tests for instance methods of classes:
        Searcher, Search

    Also is used to test relating features (like look ups from inside negamax, e.g.)
    """

    def test_opening_book_usage(self):
        """
        Tests if Search.iterative_deepening is using opening book look up at starting position.
        Tests against c4, d4, e4 (best by test) moves.
        :return:
        """
        thread = Search(state=chess.Board())
        thread.look_up_end_game = True
        decision = None
        for move in thread.iterative_deepening(thread.state, 10):
            decision = move
        possible_moves = ['e2e4', 'd2d4', 'c2c4']
        self.assertIn(str(decision), possible_moves)

    def test_endgame_db_usage(self):
        """
        Tests if Search.iterative_deepning (or lower methods) is (are) using end game look up.
        Tests against an KP-KR end game with a 7th rank pawn. Resulting evaluation is, that the
        pawn will queen because the rook and king are not correctly placed to prevent the king from
        protecting the pawn.

        The resulting KQ-KR end game is winning for the queen. Material evaluation at this point
        would give the opposite result of the correct evaluation (as the pawn WILL queen). Even
        lichess' browser Stockfish only evaluates this position as -7 though. An end game tablebase
        will know if it is mate or not.
        :return:
        """
        thread = Search(state=chess.Board("8/6k1/2R5/8/8/2K5/6p1/8 w - - 0 1"))
        thread.look_up_end_game = True
        decision = None
        for move in thread.iterative_deepening(thread.state, 10):
            decision = move
        self.assertEqual(str(decision), "c6c7")

    def test_mate_in_three(self):
        """
        Tests mate in three. Searches to depth of five. If the requested move and evaluation are
        not found, the test fails. Overevalation (depths > 5) are not possible.

        Calls test_search.iterative_deenping.
        :return:
        """
        fen = "r7/3bb1kp/q4p1N/1pnPp1np/2p4Q/2P5/1PB3P1/2B2RK1 w - - 1 0"
        self.iterative_deepening(board_representation=fen, expected_decision="h4g5", max_depth=5)

    def test_mate_in_two(self):
        """
        Tests mate in two. Absolutely the same as test_search.test_mate_in_three.

        Calls test_search.iterative_deepening.
        :return:
        """
        fen = "8/2k2p2/2b3p1/P1p1Np2/1p3b2/1P1K4/5r2/R3R3 b - - 0 1"
        self.iterative_deepening(board_representation=fen, expected_decision="c6b5", max_depth=3)

    @unittest.skip("Takes to long")
    def test_positions_iterative_deepening(self):
        """
        Takes a bunch of mating studys from a test_data.pkl'd pandas.DataFrame.
        The creation of this test_data.pkl can be found in scripts.test_set_generation.
        Test data contains mate in 5 tasks, which take very long to calculate if the engine is weak.

        Skipped:
            Because test takes to long to run for regular execution (TDD).
            Also it does not test anything that is not already tested through test_mate_in_three or
            test_mate_in_two.
        :return:
        """
        data_frame = pd.read_pickle("test_data.pkl")
        data_frame.reset_index(inplace=True)
        for _, row in data_frame.iterrows():
            print("\n\nTag of Position: {}\n".format(row["tag"]))
            self.iterative_deepening(board_representation=row["position"],
                                     expected_decision=row["best_move"],
                                     max_depth=row["moves"])

    def test_mate_in_23(self):
        """
        KNB-K end game. A good chess player that does not know the precise technique to win this,
        WILL not will this position. Position starts with the King already in the opposite corner.
        From here, it is a classic 20-25 move checkmate.

        Not knowing how to check mate here happens to the best of them ;)
            https://www.youtube.com/watch?v=YFF5ibgB6eA

        Method tests if engine is able to solve this position (or to just look it up).

        Sample solution (not exact defense):
            1. Kc6 Ka8 2. Nc7+ Kb8 3. Bb6 Kc8 4. Ba7 Kd8
            5. Nd5 Ke8 6. Kd6 Kf7 7. Ne7 Kg7 8. Be3 Kf7
            9. Bd4 Kf8 10. Ke6 Ke8 11. Bb6 Kf8 12. Nf5 Ke8
            13. Ng7+ Kf8 14. Kf6 Kg8 15. Kg6 Kh8 16. Bd8 Kg8
            17. Be7 Kh8 18. Nf5 Kg8 19. Nh6+ Kh8 20. Bf6#
        :return:
        """
        board = chess.Board("1k6/8/1K6/1NB5/8/8/8/8 w - - 0 1")
        self.iterative_deepening(board_representation=board.fen(),
                                 expected_decision="b6c6", max_depth=47)

    def iterative_deepening(self, board_representation,
                            expected_decision, max_depth=10):
        """
        Helping method for testing searching.Search.iterative_deepning.
        Creates Search-Object, runs iterative_deeping (taking the time), prints the PV.

        :param board_representation: Board to search at.
        :param expected_decision: Decision to be expected after searching to max_depth.
        :param max_depth: Depth to search at maximum.
        :return: nothing, performs assertion
        """
        board = chess.Board(board_representation)
        thread = Search(state=board, transposition_table=transpositions.TranspositionTable())
        thread.look_up_end_game = True
        start_time = time.time()
        suggestions = list(thread.iterative_deepening(state=board, max_depth=max_depth))
        self.logger.info("PV: %s",
                         [str(move) for move in
                          transpositions.get_prime_line(board, thread.transposition_table)])
        self.logger.info("Time passed since start of search: %s", time.time() - start_time)
        self.assertEqual(expected_decision, str(suggestions[-1]))

    def test_quiesce_search(self):
        """
        Tests the quiesce method
        """
        board = chess.Board("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
        searcher = Search()
        self.assertEqual(searcher.quiesce(board, -1000000, 1000000), 565)

        board = chess.Board("r7/3bb1kp/q4p1N/1pnPp1np/2p4Q/2P5/1PB3P1/2B2RK1 w - - 1 0")
        searcher = Search()
        self.assertEqual(searcher.quiesce(board, -1000000, 1000000), -550)


if __name__ == '__main__':
    unittest.main()
