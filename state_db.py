#%%
from typing import Dict, Tuple
from players import PlayAlgorithm
from gamestate import (
    Player,
    BoardState,
    GameResult,
    make_move,
    new_game,
    get_game_status,
)

DATABASE_FILE = "states.db"


class DBPlayer(PlayAlgorithm):
    """ Player using stored moves from a database. """

    def __init__(self, play_as: Player = Player.X):
        self.state_db = load_db()
        super().__init__(play_as)

    def get_move(self, state: BoardState) -> int:
        i_state = _state_to_int(state)

        return self.state_db[i_state]


# Functions for storing state information as an integer.

# Each square is coded with two bits: 00=empty, 01=X, 10=O and  the best move
# for the state is stored starting from bit 20 using 4 bits.

# In a 32 bit integer the state (squares 1-9 and the move MMMM) is stored as:
# 0000 0000 MMMM 0099 8877 6655 4433 2211

# The highest byte (top 8 bits) is unused, so in the db file each state takes
# 3 bytes


def _state_to_int(state: BoardState):
    state = list(map(lambda n: 2 if n == -1 else n, state))
    i_state = 0
    for i in range(0, 9):
        n = state[i] << (i * 2)
        i_state = i_state | n

    return i_state


def _int_to_state(i_state: int) -> BoardState:
    mask = 3  # binary "11"
    state: BoardState = []
    for i in range(0, 9):
        n = i_state & (mask << (i * 2))
        n = n >> (i * 2)
        state.append(n)

    state = list(map(lambda n: -1 if n == 2 else n, state))
    return state


# Functions for storing a move in an integer

MOVE_OFFSET = 20


def _clear_move(i_state: int) -> int:
    # 15 = 1111, so the mask after inversion is
    # 1111 1111 0000 1111 1111 1111 1111 1111
    mask = ~(15 << MOVE_OFFSET)
    return i_state & mask


def _save_move(i_state: int, move: int) -> int:
    i_state = _clear_move(i_state)
    move = move << MOVE_OFFSET
    return i_state | move


def _read_move(i_state: int) -> int:
    mask = 15 << MOVE_OFFSET
    return (i_state & mask) >> MOVE_OFFSET


def bprint(i: int, n_bits: int):
    """ Print a human readable binary representation of an int. """
    bins = bin(i)[2:].zfill(n_bits)
    print(list(map("".join, list(zip(*[iter(bins)] * 4)))))


def load_db() -> Dict[int, int]:
    """ Load best moves from a file to a dictionary. """
    db: Dict[int, int] = {}

    with open(DATABASE_FILE, "rb") as f:
        b = f.read(3)
        while b:
            i = int.from_bytes(b, byteorder="big")
            move = _read_move(i)
            i = _clear_move(i)
            db[i] = move
            b = f.read(3)

    return db


def build_db():
    """ Find and store the best move for each state using Minimax. """

    def _maximize(state: BoardState, depth: int) -> Tuple[int, int]:
        max_value = -20
        max_move = 0

        status, winner, allowed_moves = get_game_status(state)

        if not status == GameResult.Ongoing:
            return _get_value(status, winner, depth)

        for move in allowed_moves:

            make_move(state, move, play_as)
            (v, _) = _minimize(state, depth + 1)

            if v > max_value:
                max_value = v
                max_move = move

            # Revert this move
            make_move(state, move, Player.Empty)

        i_state = _state_to_int(state)
        i_state = _save_move(i_state, max_move)
        saved_states.append(i_state)

        return (max_value, max_move)

    def _minimize(state: BoardState, depth: int) -> Tuple[int, int]:

        min_value = 20
        min_move = 0

        status, winner, allowed_moves = get_game_status(state)

        if not status == GameResult.Ongoing:
            return _get_value(status, winner, depth)

        for move in allowed_moves:

            make_move(state, move, opponent)
            (v, _) = _maximize(state, depth + 1)

            if v < min_value:
                min_value = v
                min_move = move

            make_move(state, move, Player.Empty)

        return (min_value, min_move)

    def _get_value(status: GameResult, winner: Player, depth: int) -> Tuple[int, int]:
        if status == GameResult.Tie:
            return (0, 0)
        if winner == play_as:
            return (10 - depth, 0)
        return (-10 + depth, 0)

    saved_states = []

    game = new_game()

    print("Building max tree for X ...")
    play_as = Player.X
    opponent = Player.O

    _, _ = _maximize(game, 0)

    print("Building max tree for O ...")
    play_as = Player.O
    opponent = Player.X

    for i in range(0, 9):  # All starting moves for X
        make_move(game, i, opponent)
        _, _ = _maximize(game, 0)
        make_move(game, i, Player.Empty)

    print("Saving database ...")

    ss = set(saved_states)

    with open(DATABASE_FILE, "wb") as sdb:
        for i in ss:
            b = i.to_bytes(3, byteorder="big")
            sdb.write(b)

    print("Done.")