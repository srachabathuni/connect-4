import sys
import connect4


def play(board):
    board.print_board()
    while True:
        player = board.next_player
        if board.is_full():
            print("No more moves")
            sys.exit(0)

        while True:
            print(f"Player: {connect4.PLAYER_TEXT[player]}")
            try:
                userin = input("Enter column: ")
            except:
                return
            try:
                col = int(userin.strip())
                break
            except ValueError:
                print("Invalid entry")
                continue

        ret = board.play_check_win(col)
        board.print_board()
        if ret == connect4.WIN_FOUND:
            print(f"Player {connect4.PLAYER_TEXT[player]} won!")
            return


board = connect4.Board()
if len(sys.argv) > 1:
    movestr = sys.argv[1]
    strmoves = movestr.split(', ')
    moves = []
    for c in strmoves:
        moves.append(int(c))
    board.forward(moves)
play(board)
print("\nMove stack:")
print(board.move_stack)


