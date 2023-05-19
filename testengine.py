import connect4


def test_moves(moves):
    board = connect4.Board()
    board.forward(moves)
    board.print_board()

    eng = connect4.Connect4Engine(board)
    m = eng.get_best_move()
    board.play_check_win(m)
    board.print_board()


def test01():
    moves = [1, 0, 2, 3, 4, 5, 6, 6, 4, 5, 3, 2, 1, 1, 2, 1, 6, 3, 2, 5, 5]
    test_moves(moves)


def test02():
    moves = [3, 3, 4]
    test_moves(moves)


test02()
