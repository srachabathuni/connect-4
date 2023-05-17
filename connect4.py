import sys
import random
import copy

N_COLUMNS = 7
N_ROWS = 6
TO_WIN = 4

BLANK = 0
PLAYER_1 = 1
PLAYER_2 = 2 

PLAYER_TEXT = ["-", "O", "X"]


SUCCESS = 0
ERR_COLUMN_FULL = 1
ERR_INVALID_ROW = 2
ERR_INVALID_COLUMN = 3
WIN_FOUND = 4
WIN_NOT_FOUND = 5

MAX_DEPTH = TO_WIN + 1

DEBUG = False
def debug(msg):
    if DEBUG:
        print(msg)

class Board:
    def __init__(self, rows, columns, towin):
        self.columns = columns
        self.towin = towin
        self.rows = rows
        self.board = []
        self.chips_in_column = [0] * columns
        for i in range(rows):
            self.board.append([BLANK] * columns)


    def clone(self):
        new_board = Board(self.rows, self.columns, self.towin)
        new_board.board = copy.deepcopy(self.board)
        new_board.chips_in_column = self.chips_in_column.copy()
        return new_board

    def play(self, player, column):
        if self.columns <= column:
            return ERR_INVALID_COLUMN

        if self.chips_in_column[column] == self.rows:
            return ERR_COLUMN_FULL

        self.board[self.chips_in_column[column]][column] = player
        self.chips_in_column[column] += 1
        return SUCCESS


    def _check_column_win(self, player, column):
        if self.chips_in_column[column] < self.towin:
            return False

        seq = 0
        for i in range(self.chips_in_column[column]):
            if self.board[i][column] == player:
                seq += 1
                if seq == self.towin:
                    return True
            else:
                seq = 0
        return False


    def _check_row_win(self, player, column):
        seq = 0
        row = self.chips_in_column[column] - 1
        for c in range(self.columns):
            if self.board[row][c] == player:
                seq += 1
                if seq == self.towin:
                    return True
            else:
                seq = 0
        return False

    def _check_diag_win(self, player, column):
        row = self.chips_in_column[column] - 1
        # Positive slope
        if row > column:
            c = 0
            r = row - column
        else:
            r = 0
            c = column - row
        seq = 0
        while True:
            if self.board[r][c] == player:
                seq += 1
                if seq == self.towin:
                    return WIN_FOUND
            else:
                seq = 0
            r += 1
            c += 1
            if r >= self.rows or c >= self.columns:
                break

        # Negative slope
        if row > (self.columns-column-1):
            c = self.columns-1
            r = row - (self.columns - column)
        else:
            r = 0
            c = column + row
        seq = 0
        while True:
            #print(f"r: {r}, c: {c}")
            if self.board[r][c] == player:
                seq += 1
                if seq == self.towin:
                    return WIN_FOUND
            else:
                seq = 0
            r += 1
            c -= 1
            if r >= self.rows or c < 0:
                break

    def play_check_win(self, player, column):
        p = self.play(player, column)
        if p != SUCCESS:
            return p
        if self._check_column_win(player, column):
            return WIN_FOUND

        if self._check_row_win(player, column):
            return WIN_FOUND

        if self._check_diag_win(player, column):
            return WIN_FOUND

        return WIN_NOT_FOUND


    def get_chips_in_column(self, column):
        return self.chips_in_column[column]


    def is_column_full(self, column):
        return self.chips_in_column[column] == self.rows

    def is_full(self):
        for c in self.chips_in_column:
            if c < self.rows:
                return False
        return True

    def print_board(self):
        for r in range(self.rows-1, -1, -1):
            for c in self.board[r]:
                sys.stdout.write(f"{PLAYER_TEXT[c]} ")
            print("")
        for i in range(board.columns):
            sys.stdout.write(f"{i} ")
        print("")
        print("======================")


def flip_player(player):
    return PLAYER_2 if player == PLAYER_1 else PLAYER_1

class Connect4Engine:
    def __init__(self, board, player):
        self.board = board.clone()
        self.player = player

    def _get_weight(self, board, player, column, depth, max_depth, player_multiplier):
        debug(f"IN: get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
        if depth > MAX_DEPTH:
            debug(f"OUT: max_depth, get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            return 0

        nb = board.clone()
        ret = nb.play_check_win(player, column)
        if ret == WIN_FOUND:
            weight = (MAX_DEPTH - depth) * player_multiplier
            debug(f"OUT: val: {weight},  get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            return weight

        if ret == ERR_COLUMN_FULL:
            return 0

        moves = [-1000] * nb.columns
        for i in range(len(moves)):
            moves[i] = self._get_weight(nb, flip_player(player), i, depth+1, max_depth, (-1)*player_multiplier)

        if player_multiplier < 0: 
            w = max(moves) 
        else:
            w = min(moves)
        debug(f"OUT: val: {w},  get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
        return w 


    def _find_best_move(self, board, player, max_depth):
        moves = [-1000] * board.columns
        for i in range(len(moves)):
            moves[i] = self._get_weight(board, player, i, 0, max_depth, 1)
        print(f"find_best_move: {moves}")

        m = -1000
        idx = -1
        for i in range(len(moves)):
            if (not board.is_column_full(i)) and  (moves[i] > m):
                idx = i
                m = moves[i]
        
        return idx 

    def get_best_move(self):
        column = self._find_best_move(self.board, self.player, MAX_DEPTH)
        return column
        

board = Board(N_ROWS, N_COLUMNS, TO_WIN)
board.print_board()
player = PLAYER_1
while True:
    if board.is_full():
        print("No more moves")
        sys.exit(0)

    print(f"Player: {PLAYER_TEXT[player]}")
    userin = input("Enter column: ")
    col = int(userin.strip())
    ret = board.play_check_win(player, col)
    board.print_board()
    if ret == WIN_FOUND:
        print("User won!")
        sys.exit(0)

    player = flip_player(player)

    if board.is_full():
        print("No more moves")
        sys.exit(0)

    print("Thinking...")
    eng = Connect4Engine(board, player)
    move = eng.get_best_move()
    ret = board.play_check_win(player, move)
    board.print_board()
    if ret == WIN_FOUND:
        print("Computer won!")
        sys.exit(0)

    player = flip_player(player)

    # Check more moves exist


'''
board = Board(N_ROWS, N_COLUMNS, TO_WIN)
board.print_board()
player = PLAYER_1
while True:
    print(f"Player: {PLAYER_TEXT[player]}")
    userin = input("Enter column: ")
    col = int(userin.strip())
    ret = board.play_check_win(player, col)
    board.print_board()
    print(f"play_check_win: {ret}")
    if player == PLAYER_1:
        player = PLAYER_2
    else:
        player = PLAYER_1


seed = 103
random.seed(seed)
cols_full = [False] * N_COLUMNS
n_cols_full = 0
player = PLAYER_1
board = Board(N_ROWS, N_COLUMNS, TO_WIN)
while True:
    ri = random.randint(0, N_COLUMNS-1)
    if cols_full[ri]:
        continue

    print(f"Column: {ri}, Player: {PLAYER_TEXT[player]}")
    ret = board.play_check_win(player, ri)
    if ret == ERR_COLUMN_FULL:
        cols_full[ri] = True
        n_cols_full += 1
        if n_cols_full == N_COLUMNS:
            print("No winner")
            break

    board.print_board()

    if ret == WIN_FOUND:
        print("Winner found")
        break
    else:
        print("Winner NOT found")

    #input()

    if player == PLAYER_1:
        player = PLAYER_2
    else:
        player = PLAYER_1
   
'''
