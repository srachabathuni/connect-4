import sys
import random
import connect4

def get_rand_col(board):
    cols = []
    for c in range(board.columns):
        if not board.is_column_full(c):
            cols.append(c)
    return cols[random.randint(0, len(cols)-1)]

board = connect4.Board()
history = connect4.BoardHistory()
player = connect4.PLAYER_1
msg = None
while True:
    if board.is_full():
        msg = "No winner"
        break

    move = get_rand_col(board)
    ret = board.play_check_win(player, move)
    history.push(board)
    if ret == connect4.WIN_FOUND:
        msg = "Random won!"
        break

    player = connect4.flip_player(player)

    if board.is_full():
        msg = "No winner"
        break

    eng = connect4.Connect4Engine(board, player)
    move = eng.get_best_move()
    ret = board.play_check_win(player, move)
    history.push(board)
    if ret == connect4.WIN_FOUND:
        msg = "Computer won!"
        break

    player = connect4.flip_player(player)

history.print_history()
print(msg)

