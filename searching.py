"""
This file contains everything related to performing search on a given chess position.
Main class is supposed to be Searcher, which is a stoppable thread. By sending the stop message to
a stoppable thread, the thread is requested for termination. With this mechanism we want to
implement time management independently of the actual search to keep the code simple.
"""
import logging
import threading
import numpy as np
import chess

import moves
import transpositions
import catalogue
from environment import calculate_game_state, OPENING
from evaluation import SimplifiedEvaluationFunction

LOGGER = logging.getLogger("chess_logger")
SIMPLIFIED_EVAL = SimplifiedEvaluationFunction()


def actions_with_assigned_values(list_of_moves, value):
    """
    Using the fact, that in parameters are mutable objects, copied references are passed...

    :param list_of_moves: Some moves
    :param value: Some value
    :return: None
    """
    for move in list_of_moves:
        move.assigned_value = value
    return list_of_moves


class StoppableThread(threading.Thread):
    """
    A Thread that can be stopped using its stop method.
    Subclasses need to use is_stopped while performing a given task to check if they are supposed
    to quit their current work. Makes sense to be used in timed environments.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.__stop_event = threading.Event()

    def stop(self):
        """
        Call this method in order to stop the Thread!
        Taken from: https://stackoverflow.com/a/325528
        :return: None
        """
        LOGGER.debug("THREAD HAS BEEN STOPPED")
        self.__stop_event.set()

    def is_stopped(self):
        """
        Self check if the stop event was called.
        Used to find out whether or not the Thread is supposed to be stopped.
        :return: None
        """
        return self.__stop_event.isSet()


class Searcher(StoppableThread):
    """
    The class for performing the search on a given instance of chess.Board.
    It is a stoppable thread. To quit searching at a specific position is_stopped is checked often.
    Note this class is search type independent. The actuall implementation of search is supposed to
    be implemented in one of its subclasses.

    Call stop method on this class to stop it searching on the position.
    For directly following search either use a new instance of Searcher and pass it around or use
    the same instance more than once. There is no particular reason not to do the first.
    """
    def __init__(self, state=chess.Board(),
                 transposition_table=transpositions.TranspositionTable(), **kwargs):
        super().__init__(**kwargs)

        # set None accessible fields
        self.__decision_stack = []
        self.__tp = transposition_table

        # set accessible fields
        self.__state = state
        self.__score = 0
        self.__look_up_end_game = True
        self.__look_up_opening = True
        self.__evaluation = None
        self.__decision = None

    @property
    def cp_score(self):
        """
        Returns a centipawn score for uci output and value printing.
        Returned value is not used in search calculation. Hence, the rounding operation has no
        negative effects on the quality of the search.

        :return: evaluation in centipawn value
        """
        return np.round(self.score / (self.evaluation.pawn_value / 100), decimals=0)

    @property
    def look_up_end_game(self):
        """
        Determines, whether or not table look ups for opening and end game should be used.
        Generelly, the GUI provides endgame tables through the UCI, the engine should be agnostic
        to whether tables are specified or not. However, since this is only a practice, we decided
        to implement look up just for the fun of it.

        :return: boolean value whether or not engine look ups are allowed
        """
        return self.__look_up_end_game

    @look_up_end_game.setter
    def look_up_end_game(self, value):
        """
        Look up is a public attribute, because instances using Searcher need to be able to chose
        for look ups to be allowed or not. For unittesting the search algorithms, it is a good
        practice to disable look up whereas for the actual game being able to look up is a nice-to-
        have.

        :param value: boolean value to set look up property to
        :return:
        """
        self.__look_up_end_game = value

    @property
    def look_up_opening(self):
        """
        Determines, whether or not table look ups for opening and end game should be used.
        Generelly, the GUI provides endgame tables through the UCI, the engine should be agnostic
        to whether tables are specified or not. However, since this is only a practice, we decided
        to implement look up just for the fun of it.

        :return: boolean value whether or not engine look ups are allowed
        """
        return self.__look_up_opening

    @look_up_opening.setter
    def look_up_opening(self, value):
        """
        Look up is a public attribute, because instances using Searcher need to be able to chose
        for look ups to be allowed or not. For unittesting the search algorithms, it is a good
        practice to disable look up whereas for the actual game being able to look up is a nice-to-
        have.

        :param value: boolean value to set look up property to
        :return:
        """
        self.__look_up_opening = value


    @property
    def score(self):
        """
        Property to hold the score evaluated by the engine at a specific depth. Consider using
        property cp_score instead of this one for consistant logging. In cases of evaluation
        functions that use a pawn value of 10^n (n>0), this shouldn't make much of a difference
        though.

        :return: The score returned by search algorithm at the current depth.
        """
        return self.__score

    @score.setter
    def score(self, value):
        """
        Setter for score property. This is not really needed, as only subclasses need to be able
        to write to this property. They are able to access self.__score easily. However having this
        attribute public also does not hurt that much right now. Thats why we decided to keep it.

        :param value: Number to set the score variable to.
        :return:
        """
        self.__score = value

    @property
    def state(self):
        """
        Attribute for the current state (instance of chess.Board) to look at.

        :return: The state of question.
        """
        return self.__state

    @state.setter
    def state(self, value):
        """
        Setting the state to search at which must be an instance of chess.Board.
        This must be public, as unittests and TimeManager need to set this attribute.

        :param value: instance of chess.Board
        :return:
        """
        assert isinstance(value, chess.Board)
        self.__state = value

    @property
    def transposition_table(self):
        """
        Property for the transposition table assigned to each search execution. Needs to be public
        for higher classes to extract transposition table for other purposes (e.g. reuse, printing).

        :return: The instance of transpositions.TranspositionTable assigned to this instance.
        """
        return self.__tp

    @transposition_table.setter
    def transposition_table(self, value):
        """
        If the transposition table is supposed to be reused in later stages, making it public seems
        like a reasonable thing to do.

        :param value: instance of transpositions.TranspositionTable (ASSERTED)
        :return:
        """
        assert isinstance(value, transpositions.TranspositionTable)
        self.__tp = value

    @property
    def decision(self):
        """

        :return:
        """
        return self.__decision

    @decision.setter
    def decision(self, value):
        """
        Only used to write self.decision_stack automatically!

        :param value: Decision as a move to be set.
        :return:
        """
        self.decision_stack.append(value)
        self.__decision = value

    @property
    def decision_stack(self):
        """
        Having a list of all past decisions is nice!

        :return:
        """
        return self.__decision_stack

    @property
    def evaluation(self):
        """
        Property for the evaluation function assigned to each search execution.

        :return: The instance of evaluation.LinearEvaluations subclasses assigned to this instance.
        """
        return self.__evaluation

    @evaluation.setter
    def evaluation(self, value):
        """
        Higher instances need to be able to set this evaluation function to use the engine
        modularly. Therefore, it needs to be public.

        :return:
        """
        self.__evaluation = value


class Search(Searcher):
    """
    Thread for performing enhanced Minimax Search.
    Stoppable via #stop. Ensure #_stopped is checked accordingly to terminate thread.
    TODO: Parameters for actually performing a search.
    TODO: Linking Search Methods from other source files.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.evaluation = SIMPLIFIED_EVAL
        self.__current_depth = 0
        self.__game_state = calculate_game_state(self.state)

    def run(self):
        """
        Master search method. Overrides threading.Thread.run() which is the method called when a
        new thread is started. Core objective is to have ONLY this method write to self.decision!

        Used as follows:
            >>> thread = Search()
            >>> thread.start()  # leads to execution of this method

        :return: None in any case
        """
        if self.state.is_game_over():
            return
        for move in self.iterative_deepening(self.state, max_depth=100000):  # call to generator
            self.decision = move
            print("info depth {} score cp {} bestmove {}"
                  .format(self.__current_depth, self.cp_score, self.decision))
            # if len(self.decision_stack) > 2:  # abort search if change is unlikely
            #     if all(x == self.decision_stack[-1] for x in self.decision_stack[-3:-1]):
            #         self.stop()

    def iterative_deepening(self, state, max_depth):
        """
        Iterative deepening depth limited alpha beta search implemenation.
        Calls submethod alpha_beta_search which will call negamax eventually.

        This method performs opening lookups as it is unlikely, that opening look ups will be
        necessary at increasing search depth. End game lookup is performed by negamax.

        :param state: current state to look up
        :param max_depth: maxium depth after which the search should be aborted
        :return:
        """
        self.__game_state = calculate_game_state(state)
        if self.look_up_opening and self.__game_state == OPENING:
            opening_book_move = catalogue.opening_lookup(state)
            if opening_book_move is not None:
                self.stop()
                yield opening_book_move
                return
        self.__current_depth = 0
        decision = list(state.legal_moves)[0]
        while True:
            self.__current_depth += 1
            move, self.score = self.alpha_beta_search(state, self.__current_depth)
            if not self.is_stopped():
                decision = move
                LOGGER.debug("decision %s depth %s score %s table entries %s",
                             str(decision), self.__current_depth, self.cp_score,
                             len(self.transposition_table))
                yield decision
            if self.is_stopped() or self.__current_depth > max_depth:
                return
            if self.score in (100000, -100000):
                return

    def alpha_beta_search(self, state, depth_limit):
        """
        Master method for negamax search. Implements interface between negamax and iterative
        deepening methods.

        :param state: state to let negamax search at
        :param depth_limit: depth to let negamax search at the current state
        :return: value caught from self.transposition_table for state
        """
        value = self.negamax(state, depth=depth_limit, alpha=-float("inf"), beta=float("inf"))
        return self.transposition_table[state].moves[0], value

    def negamax(self, state, depth, alpha, beta):
        """
        Method for performing the search using alpha beta search in a negamax framework.

        :param state: Current state to search at.
        :param depth: Depth to search searchtree(state) at.
        :param alpha: Current lower bound value for player(state).
        :param beta: Current upper bound value for player(state).
        :return:
        """
        alpha_original = alpha

        try:
            stored_data = self.transposition_table[state]
            if stored_data.depth >= depth:
                if stored_data.node_type == transpositions.PV_NODE or alpha >= beta:
                    return stored_data.score
                if stored_data.node_type == transpositions.ALL_NODE:
                    alpha = max(alpha, stored_data.score)
                elif stored_data.node_type == transpositions.CUT_NODE:
                    beta = min(beta, stored_data.score)
        except KeyError:  # no entry in self.transposition_table found -> create new one
            stored_data = transpositions.TranspositionTableEntry()

        # determine factor to compensate negamax
        factor = (1 if state.turn else -1)

        # perform fast search end if search was stopped
        if self.is_stopped():
            return self.evaluation[state] * factor

        # return utility if game ends
        if state.is_game_over():
            return self.evaluation[state] * factor

        # perform end game table look up (only if self.look_up_end_game)
        if self.look_up_end_game and len(state.piece_map()) <= catalogue.MAX_GAVIOTA_PIECES:
            # pylint: disable=broad-except
            #  This exception is logged anyway. Removing this warning is therefore reasonable.
            try:
                return self.end_game_lookup(state, stored_data, factor)
            except Exception as exception:
                LOGGER.exception("Exception on lookup: %s", exception.with_traceback())

        # call quiesce at depth cut off
        if depth == 0:
            return self.quiesce(state, alpha, beta)

        # searching through child nodes
        actions = actions_with_assigned_values(moves.prioritized(state), value=-100001)\
            if stored_data.moves is None else stored_data.moves
        for action in actions:
            state.push(action)
            action.assigned_value = - self.negamax(state, depth - 1, -beta, -alpha)
            state.pop()
            if action.assigned_value >= beta:
                alpha = beta
                break
            if action.assigned_value > alpha:
                alpha = action.assigned_value
        actions.sort(key=lambda x: x.assigned_value, reverse=True)

        if not self.is_stopped():  # write to self.transposition_table
            stored_data.fill(score=alpha, depth=depth, moves=actions)
            stored_data.calc_node_type(alpha_original, beta)
            self.transposition_table[state] = stored_data
        return alpha

    def end_game_lookup(self, state, stored_data, factor):
        """
        Method for looking up moves in the end game. Handles transposition table entry and returns
        value caught. Throws exception (most likely some Gaviota Table Not Found ones or just plain
        KeyErrors) if something went wrong.

        :param state: State to look up at (like <6 pieces)
        :param stored_data: current TranspositionTableEntry
        :param factor: from negamax framework indicating what the value should be multiplied with
        :return:
            1 if white wins
            -1 if black wins
            0 if game will be drawn at precise play
        """
        value = 100000 * catalogue.get_endgame_wdl(state) * factor
        move = catalogue.endgame_lookup(state)  # costly
        stored_data.fill(score=value, depth=float("inf"), moves=[move])
        self.transposition_table[state] = stored_data
        return value

    def quiesce(self, state, alpha, beta):
        """
        Method for returning a score at depth cut off using Quiescence Search.

        :param state: Current state to search at.
        :param alpha: Current lower bound value for player(state).
        :param beta: Current upper bound value for player(state).
        :return:
        """
        # determine factor to compensate negamax
        factor = (1 if state.turn else -1)

        # evaluate the base value for current state
        current_value = self.evaluation[state] * factor
        if current_value > beta:
            return beta
        if alpha < current_value:
            alpha = current_value

        # get best capturing move and get its score
        best_capture = moves.best_move_for_rest_search(state)
        if best_capture is None:
            return alpha
        state.push(best_capture)
        new_score = -self.quiesce(state, -beta, -alpha)
        state.pop()
        if new_score >= beta:
            return beta
        if new_score > alpha:
            alpha = new_score
        return alpha
