import random
import connect4


board = connect4.Board()
first_move_col = random.randint(0, board.columns-1)
board.play(first_move_col)
msg = None
while True:
    if board.is_full():
        msg = "No winner"
        break

    eng = connect4.Connect4Engine(board)
    move = eng.get_best_move()
    ret = board.play_check_win(move)
    if ret == connect4.WIN_FOUND:
        msg = f"{board.get_last_player()} won"
        break
    if board.is_full():
        msg = "No winner"
        break

    eng = connect4.Connect4Engine(board)
    move = eng.get_best_move()
    ret = board.play_check_win(move)
    if ret == connect4.WIN_FOUND:
        msg = f"{board.get_last_player()} won"
        break

board.print_board()
