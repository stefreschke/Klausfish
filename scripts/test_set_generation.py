"""
Generating some mating tasks.
"""
from pandas.io.json import json_normalize


ARRAY = [
    {
        "position": "r7/3bb1kp/q4p1N/1pnPp1np/2p4Q/2P5/1PB3P1/2B2RK1 w - - 1 0",
        "best_move": "h4g5",
        "tag": "Mate in 3",
        "moves": 5
    },
    {
        "position": "8/2k2p2/2b3p1/P1p1Np2/1p3b2/1P1K4/5r2/R3R3 b - - 0 1",
        "best_move": "c6b5",
        "tag": "Mate in 2",
        "moves": 3
    },
    {
        "position": "r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1",
        "best_move": "f3f7",
        "tag": "Mate in 1",
        "moves": 1
    },
    {
        "position": "7R/r1p1q1pp/3k4/1p1n1Q2/3N4/8/1PP2PPP/2B3K1 w - - 1 0",
        # Keres Salamanca, 1943
        "best_move": "h8d8",
        "tag": "Mate in 4",
        "moves": 7
    },
    {
        "position": "6k1/3b3r/1p1p4/p1n2p2/1PPNpP1q/P3Q1p1/1R1RB1P1/5K2 b - - 0 1",
        # Keres Petrosian, 1959
        "best_move": "h4f4",
        "tag": "Mate in 5",
        "moves": 9
    },
    {
        "position": "2q1nk1r/4Rp2/1ppp1P2/6Pp/3p1B2/3P3P/PPP1Q3/6K1 w k - 0 1",
        "best_move": "e7e8",
        "tag": "Mate in 5",
        "moves": 9
    }
]


def create_dataframes():
    """
    Write test data pandas.DataFrame.

    :return: DataFrame.
    """
    data_frame = json_normalize(ARRAY)
    data_frame.set_index("position", inplace=True)
    return data_frame


def save_files(data_frame, name):
    """
    Pickles DataFrames to files.

    :param data_frame: DataFrame
    :param name: filename (without csv, that is added)
    :return: Nothing
    """
    data_frame.to_pickle("{}.pkl".format(name))
    data_frame.to_csv("{}.csv".format(name), sep=";", decimal=",")


if __name__ == '__main__':
    save_files(create_dataframes(), "test_data")
