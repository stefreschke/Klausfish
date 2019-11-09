"""
File that contains anything related to managing time. Since time is a vital aspect of the game of
chess (except for correspondence games), it is useful to manage it.

Therefore we provide the class Clock and TimeManager. Clock is used to keep track of an actual
chess clock and is, in a sense, a proxy for an imaginary one. The Time Manager keeps looking at a
clock (which is one of his attributes) and decides how much time to spend on one move. Based on this
calculation, the search is started (time boxed).
"""
import sched
import time
import copy
import numpy as np
import searching
import transpositions


class Clock:
    """
    Class for keeping track of a chess clock.
    Is able to provide features for Fischer and Bronstein increment, as well as Delay.
    Also provides methods for taking time of the clock.
    """
    def __init__(self, base_time=5*60*1000, unconditional_increment=0, conditional_increment=0,
                 delay=0, **next_time_controls):
        self.__base_time = base_time
        self.__unconditional_increment = unconditional_increment
        self.__conditional_increment = conditional_increment
        self.__delay = delay
        for move_number, time_control in next_time_controls.items():
            if not (isinstance(move_number, int) and isinstance(time_control, Clock)):
                raise AttributeError("Invalid following time controls where given")
        self.next_time_controls = next_time_controls

    @property
    def base_time(self):
        """
        Base_time is the remaining time visible on the clock. It can be read from the outside.
        Therefor this property should be publically readable.
        :return:
        """
        return self.__base_time

    @base_time.setter
    def base_time(self, value):
        """
        Time can pass. Hence the time can be changed publically.
        :param value: New value to set time to.
        :return:
        """
        self.__base_time = value

    @property
    def unconditional_increment(self):
        """
        Increment as proposed by Fischer. Chess clock needs to store time information, therefore it
        also has to have a property for the unconditional increment awarded each move.
        :return:
        """
        return self.__unconditional_increment

    @property
    def conditional_increment(self):
        """
        Increment as proposed by Bronstein. Chess clock needs to store time information, therefore
        it also has to have a property for the conditional increment awarded each move based on the
        time spent.
        :return:
        """
        return self.__conditional_increment

    @property
    def delay(self):
        """
        Sort of the new "hip" way of playing with increment. Clock starts with a delay of some time.
        Chess clock needs to store time information, therefore it also has to have a property for
        the delay the time should start running at.
        :return:
        """
        return self.__delay


class TimeManager:
    """
    Class for managing time during a chess game.
    Basically handles all other aspect of the engine.
    Accessed through uci.py!
    """
    def __init__(self, time_control=Clock(), moves_to_go=40):
        self.time_control = time_control
        self._original_time_control = copy.deepcopy(time_control)
        self.moves_to_go = moves_to_go
        self.__transposition_table = transpositions.TranspositionTable()
        self.__decision = None
        self.__done = False

    @property
    def decision(self):
        """
        Decision (from Searcher instance) that could be calculated to be good in the given time.
        Time manager needs to have this as a property, because higher leveled modules (user
        interfaces) only access time manager to get this information.
        :return:
        """
        return self.__decision

    @property
    def transposition_table(self):
        """
        Having the transposition_table as a property of the TimeManager makes it possible for the
        transposition table to be kept for further search tasks. Right now this it not used, but it
        might come in handy in the future. Thats why we decided to implement this property.
        :return:
        """
        return self.__transposition_table

    @property
    def done(self):
        """
        Boolean value indicating whether or not the TimeManager is done searching the given state.
        GUI needs to busy wait for this attribute to be true! Thats why property access is granted.
        :return:
        """
        return self.__done

    def info_from_uci(self, wtime=1, winc=0, binc=0, movestog=1, infinite=False,
                      **kwargs):
        """
        Retrieve current clock information from UCI.

        :param wtime: remaining time
        :param winc: fischer increment
        :param binc: bronstein increment
        :param movestog: remaining moves til next time control
        :param infinite: whether the search should be infinite (overrules wtime)
        :param kwargs: other parameters used by UCI (are currently disregarded)
        :return:
        """

        if infinite:
            wtime = 10e7  # dirty workaround
        self.time_control = Clock(wtime, winc, binc, 0)
        self.moves_to_go = movestog if movestog is not None else self.moves_to_go

    def new_game(self):
        """
        Method to reset the clock. Copies the originally created deepcopy once more and rewrites it
        to the time_control attribute.
        :return:
        """
        self.time_control = copy.deepcopy(self._original_time_control)

    def spent_time(self, amount):
        """
        Reduce the time on the clock by a certain amount.
        This might be used for different reasons (e.g. to compensate software response time).

        :param amount: The amount to reduce the time on the clock by.
        :return:
        """
        self.time_control.base_time -= amount

    def allocate_time(self):
        """
        Returns a number of maximum time, that should be used for a move.
        Later used to give a max time used. Will produce cut_off accordingly.

        :return: SECONDS: The amount of time available for searching a move on the board.
        """
        available = self.time_control.base_time / 1000
        return np.min([np.floor(available / self.moves_to_go)
                       + self.time_control.unconditional_increment / 1000
                       + self.time_control.conditional_increment / 1000, available * 0.5])

    def perform_search(self, board, look_up_in_opening=True, look_up_in_end_game=False):
        """
        Allocate time for the given board and run search for exactly that amount of time.
        Primary interface method of this class!

        :param board: The position (instance of chess.Board) to search at.
        :param look_up_in_opening: Whether or not looking up should be allowed in opening.
        :param look_up_in_end_game: Whether or not looking up should be allowed in end game.
        :return:
        """
        self.__done = False
        allocated_time = self.allocate_time()
        self.spent_time(amount=allocated_time)
        self.run_searcher_for(allocated_time, on_board=board,
                              look_up_in_opening=look_up_in_opening,
                              look_up_in_end_game=look_up_in_end_game)
        self.__done = True

    def run_searcher_for(self, seconds, on_board, look_up_in_opening, look_up_in_end_game):
        """
        Using sched module to make sure the search is stopped at the correct time.
        This way it is not necessary to create tiny helping threads, which was used in the former
        release (and didn't quite work so good).

        :param seconds: How long the search should run before being cancelled.
        :param on_board: The position (instance of chess.Board) to search at.
        :param look_up_in_opening: Whether or not look up in data base is allowed in the opening.
        :param look_up_in_end_game: Whether or not look up in data base is allowed in end game.
        :return:
        """
        thread = searching.Search(state=on_board, transposition_table=self.transposition_table)
        thread.look_up_end_game = look_up_in_end_game
        thread.look_up_opening = look_up_in_opening
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(delay=0, priority=1, action=thread.start)
        scheduler.enter(delay=seconds, priority=1, action=thread.stop)
        scheduler.run(blocking=True)
        self.__decision = thread.decision
        self.__transposition_table = thread.transposition_table
