"""
Testing python chess using Perft. See: https://www.chessprogramming.org/Perft
We also used this test to check if our alpha beta is actually reducing the tree or if it is
watching the whole one. Turns out alpha beta was working. (y)
"""
import unittest
import time
import chess
import moves
import test_baseclass


PERFT_VALUES = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 ": [1, 20, 400, 8902, 197281],
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1": [1, 48, 2039, 97862,
                                                                             4085603],
    "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8": [1, 44, 1486, 62379, 2103487]
}


class PerftTest(test_baseclass.ChessTest):
    """
    Class used for all perft test related methods.
    """

    # pylint: disable=missing-docstring

    def test_perft(self, max_depth=3):
        """
        Perft-testing the move generation in order to make sure there is no easy bug there.
        :return:
        """
        for fen, expectations in PERFT_VALUES.items():
            state = chess.Board(fen)
            for i in range(min(len(expectations), max_depth)):
                nodes = self.perft(state=state, depth=i)
                self.logger.debug("depth %d nodes %s", i, nodes)
                self.assertEqual(expectations[i], nodes)

    def test_timing(self, position=chess.Board(), depth=3):
        """
        Timing ours used move generation generator method againts the basic generator/list.
        Assert if ours is significantly slower.

        :param position: board to look at
        :param depth: depth used to time check
        :return:
        """
        results = {}
        for label, generator in {"ours": moves.prioritized, "list": lambda x: list(x.legal_moves),
                                 "gen": lambda x: x.legal_moves}.items():
            time_used = time.time()
            self.perft(state=position, depth=depth, generator=generator)
            results[label] = time.time() - time_used
        results = list(results.items())
        results.sort(key=lambda x: x[1])
        for label, value in results:
            self.logger.info("generator {}\t spent {:3.3f}s".format(label, value))
        factor_between = results[-1][1] / results[0][1]
        self.assertLess(factor_between, 1.3)  # not 30% worse than the best (would mean a bug)

    # Non testing method (see https://www.chessprogramming.org/Perft)
    def perft(self, state, depth, generator=moves.prioritized):
        """
        Method used for checking the number of nodes.
        Used to find bugs in move generation.
        Taken from C code from: https://www.chessprogramming.org/Perft_Results

        :param state: state to look at
        :param depth: depth to look at
        :param generator: Lambda used to get moves from board
        :return:
        """
        nodes = 0
        if depth == 0:
            return 1
        mvs = generator(state)
        for moverinho in mvs:
            state.push(moverinho)
            nodes += self.perft(state, depth - 1)
            state.pop()
        return nodes




if __name__ == '__main__':
    unittest.main()
