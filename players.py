import random
from typing import List, Tuple
from gamestate import *


class PlayAlgorithm:
    """ Interface for player implementations. """

    def __init__(self, play_as: Player = Player.X):
        self.play_as = play_as
        if play_as == Player.X:
            self.opponent = Player.O
        else:
            self.opponent = Player.X

    def get_move(self, state: BoardState) -> int:
        ...


class RandomPlayer(PlayAlgorithm):
    """ Player that selects moves randomly. """

    def get_move(self, state: BoardState) -> int:
        _, _, allowed_moves = get_game_status(state)
        return random.choice(allowed_moves)


class MinimaxPlayer(PlayAlgorithm):
    """ Player using the minimax algorithm and optionally alpha-beta pruning. """

    def __init__(
        self,
        play_as: Player = Player.X,
        use_pruning: bool = True,  # Use alpha-beta pruning
        use_depth: bool = True,  # Use move depth as part of state score
    ):
        self.use_pruning = use_pruning
        self.use_depth = use_depth
        super().__init__(play_as)

    def get_move(self, state: BoardState) -> int:
        # Start in the corner for faster start
        if not (1 in state or -1 in state):
            return 0

        _, max_move = self._maximize(state, 0)
        return max_move

    def _maximize(
        self, state: List[int], depth: int, alpha: int = -20, beta: int = 20
    ) -> Tuple[int, int]:

        max_value = -20
        max_move = 0

        status, winner, allowed_moves = get_game_status(state)

        if not status == GameResult.Ongoing:
            return self._get_value(status, winner, depth)

        for move in allowed_moves:

            make_move(state, move, self.play_as)
            (v, _) = self._minimize(state, depth + 1, alpha, beta)

            if v > max_value:
                max_value = v
                max_move = move

            # Revert this move
            make_move(state, move, Player.Empty)

            if self.use_pruning:
                if max_value >= beta:
                    return (max_value, max_move)

                if max_value > alpha:
                    alpha = max_value

        return (max_value, max_move)

    def _minimize(
        self, state: List[int], depth: int, alpha: int = -20, beta: int = 20
    ) -> Tuple[int, int]:

        min_value = 20
        min_move = 0

        status, winner, allowed_moves = get_game_status(state)

        if not status == GameResult.Ongoing:
            return self._get_value(status, winner, depth)

        for move in allowed_moves:

            make_move(state, move, self.opponent)
            (v, _) = self._maximize(state, depth + 1, alpha, beta)

            if v < min_value:
                min_value = v
                min_move = move

            make_move(state, move, Player.Empty)

            if self.use_pruning:
                if min_value <= alpha:
                    return (min_value, min_move)

                if min_value < beta:
                    beta = min_value

        return (min_value, min_move)

    def _get_value(self, status, winner, depth) -> Tuple[int, int]:
        if status == GameResult.Tie:
            return (0, 0)

        if winner == self.play_as:
            if self.use_depth:
                # Faster win is better
                return (10 - depth, 0)
            else:
                return (10, 0)

        if self.use_depth:
            # Slower loss is better
            return (-10 + depth, 0)
        else:
            return (-10, 0)
