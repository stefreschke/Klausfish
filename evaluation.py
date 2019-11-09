"""
This file is supposed to contain everything related to performing evaluation on a state.
Aggregates heuristics.py accordingly.

Main feature of this file is the LinearEvaluation class whose subclasses can be used to save a
specific evaluation mixture, combining features functions and weights by adding their products
together.
"""
import logging
import chess
import numpy as np
import heuristics
from environment import utility

LOGGER = logging.getLogger("chess_logger")


class LinearEvaluation:
    """
    Class for managing a linear evaluation function.
    Uses the dictionary protocol to shorten code. Instance method calculate is called accordingly.

    Say LE is an instance of LinearEvaluation, s is an instance of chess.Board:
        LE[s] returns the evaluation of this position.
        LE[s] is the short form for LE.calculate(s)

    Fields:
        features = List of lambda functions (1 function = 1 feature)
        weights = List of numbers (first weight is assigned to first feature in features)
        pawn_value
    """
    def __init__(self):
        self.features = []
        self.weights = []
        self.pawn_value = 1

    def add_feature(self, feature, weight=1.0):
        """
        Adds a given Feature to the features list.

        :param feature: The feature that should be added.
        :param weight: The weight the feature should be applied to the total sum.
        :return: None
        """
        self.features.append(feature)
        self.weights.append(weight)
        self.check_consistency()
        LOGGER.debug("Added new feature to evaluation. Now has %d entries", len(self.features))

    def remove_feature(self, index):
        """
        Removes a feature from the feature list.

        :param index: A valid index of a feature from the feature list.
        :return: None
        """
        if self.check_valid_index(index):
            self.features.pop(index)
            self.weights.pop(index)
            LOGGER.debug("Removed feature")
        else:
            LOGGER.error("Removing of a feature has failed")

    def calculate(self, state):
        """
        Performs the actual calculation by calling all features with a given state.

        :param state: State the weighted linear evaluation function is supposed to be called with
        :return: ...a numberish value.
        """
        if state.is_game_over():
            return utility(state)
        return np.sum([self.features[i](state) * self.weights[i]
                       for i in range(len(self.features))])

    def __getitem__(self, key):
        """
        Fancy override of dictionary key selection protocol.
        Makes code more short, but also possibly confusing.

        :param key: State self.calculate should be called with.
        :return: self.calculate(key)
        """
        return self.calculate(key)

    def __setitem__(self, key, val):
        pass

    def check_valid_index(self, index):
        """
        Check if the index is valid.
        Index is valid if both weight and feature exist for it.
        :param index:
        :return:
        """
        return 0 <= index < len(self.features)

    def check_consistency(self):
        """
        Check if there is an equal number of features and weights.
        :return: nothing
            raises EnvironmentError if the number is invalid
        """
        if len(self.features) != len(self.weights):
            raise EnvironmentError("Not equal number of features and weights in evaluation")


class SimplifiedEvaluationFunction(LinearEvaluation):
    """
    Simplified evaluation function.
    Only uses material values and simple piece squared tables.
    """

    material_values = {  # material values for simplified evaluation function
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    def __init__(self):
        super().__init__()
        self.pawn_value = self.material_values[chess.PAWN]
        # needed because searching.Searcher.cp_score
        self.add_feature(feature=self.material_heuristic, weight=1)
        self.add_feature(feature=heuristics.piece_squared_tables, weight=1)

    @staticmethod
    def material_heuristic(state, values=material_values):
        """
        Just a static class method - feature for reflecting self.material_values into heuristics.
        material_heuristic_fast.

        :param state: Position to apply the feature to.
        :param values: Only needed for default value. Do not worry.
        :return:
        """
        # pylint: disable=dangerous-default-value
        #  can be disabled, because change of this argument is not really possible
        return heuristics.material_heuristic_fast(state, values)
