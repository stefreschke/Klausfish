"""
Basic stuff used for unittesting the engine within ./tests/ subdirectory of this repository.
"""
import unittest
import logging


class ChessTest(unittest.TestCase):
    """
    Base class used for all unittest envolving chess components.
    Initializes the chess_logger through logging. Therefore implements setUp and tearDown for unit
    test protocol.

    Superclasses that need to write their own setUp or tearDown need to call (respectively):
        super().setUp()
        super().tearDown()
    """
    def initialize_logging_handler(self):
        """
        Method used to generate the actual logging handler for chess unit tests.
        Note that this handler needs to be removed after the test during tearDown.
        :return:
        """
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.DEBUG)
        self._ch.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                                datefmt='%Y-%m-%d %H:%M:%S'))

    def setUp(self):
        self.initialize_logging_handler()
        mc_logger = logging.getLogger('chess_logger')
        mc_logger.setLevel(logging.DEBUG)
        mc_logger.addHandler(self._ch)
        self.logger = mc_logger

    def tearDown(self):
        mc_logger = logging.getLogger('chess_logger')
        mc_logger.removeHandler(self._ch)
        del mc_logger
        del self.logger
