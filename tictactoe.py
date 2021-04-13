#%%
from gamestate import *
from players import RandomPlayer, MinimaxPlayer
from state_db import DBPlayer
import time


p1 = MinimaxPlayer(Player.X, use_pruning=True, use_depth=True)
# p1 = DBPlayer(Player.X)
p2 = RandomPlayer(Player.O)

start = time.time()

stats = {Player.X: 0, Player.O: 0, Player.Empty: 0}
rounds = 1000
moves = 0

print("Playing...")

for _ in range(0, rounds):

    board = new_game()
    player_in_turn = Player.X

    status = get_game_status(board)
    while status.result == GameResult.Ongoing:

        if p1.play_as == player_in_turn:
            m = p1.get_move(board)
        else:
            m = p2.get_move(board)

        make_move(board, m, player_in_turn)
        moves += 1

        if player_in_turn == Player.X:
            player_in_turn = Player.O
        else:
            player_in_turn = Player.X

        status = get_game_status(board)

    stats[status.winner] += 1

end = time.time()

print(
    f"Played {rounds} rounds. X wins: {stats[Player.X]}, O wins: {stats[Player.O]}, ties: {stats[Player.Empty]}."
)

print(f"Avg. moves per round: {moves / rounds}")
print(f"Total time: {end - start} s")