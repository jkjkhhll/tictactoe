#%%
from enum import IntEnum
from typing import List, NamedTuple

# Board state is stored as a list of ints, where 0 = empty square, 1 = 'X' and -1 = 'O'.
# This for easy calculations since row / column / diagonal sum of 3 means X wins and
#  -3 means O wins
BoardState = List[int]

# Used for printing
LEGEND = {0: ".", 1: "X", -1: "O"}


class Player(IntEnum):
    X = 1
    O = -1
    Empty = 0


class GameResult(IntEnum):
    Ongoing = 0
    Win = 1
    Tie = 2


class GameStatus(NamedTuple):
    result: GameResult
    winner: Player
    allowed_moves: List[int]


def new_game() -> BoardState:
    """ Start new empty game. """
    return [Player.Empty.value] * 9


def print_board(state: BoardState):
    """ Print the board state prettily to console. """
    p_state = list(map(lambda n: LEGEND[n], state))
    print(" ".join(p_state[:3]))
    print(" ".join(p_state[3:6]))
    print(" ".join(p_state[6:9]))
    print()


def get_game_status(state: BoardState) -> GameStatus:
    """ Return the current status of the game (won, tied, ongoing), the winner and any available moves. """

    # Row, column and diagonal sums
    r1, r2, r3 = 0, 0, 0
    c1, c2, c3 = 0, 0, 0
    d1, d2 = 0, 0

    allowed_moves: List[int] = []

    for i, v in enumerate(state):

        if v == 0:
            allowed_moves.append(i)

        # Rows
        if i in [0, 1, 2]:
            r1 += v
        if i in [3, 4, 5]:
            r2 += v
        if i in [6, 7, 8]:
            r3 += v

        # Columns
        if i % 3 == 0:
            c1 += v
        if i % 3 == 1:
            c2 += v
        if i % 3 == 2:
            c3 += v

        # Diagonals
        if i in [0, 4, 8]:
            d1 += v

        if i in [2, 4, 6]:
            d2 += v

    sums = [r1, r2, r3, c1, c2, c3, d1, d2]

    if 3 in sums:
        return GameStatus(result=GameResult.Win, winner=Player.X, allowed_moves=[])
    if -3 in sums:
        return GameStatus(result=GameResult.Win, winner=Player.O, allowed_moves=[])
    else:
        if len(allowed_moves) > 0:
            return GameStatus(
                result=GameResult.Ongoing,
                winner=Player.Empty,
                allowed_moves=allowed_moves,
            )
        else:
            return GameStatus(
                result=GameResult.Tie, winner=Player.Empty, allowed_moves=[]
            )


def make_move(state: BoardState, move: int, player: Player):
    """ Make a move on the board. """
    state[move] = player.value
