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

MAX_DEPTH = TO_WIN
MIN_WEIGHT = 100000
MAJOR_WEIGHT_MULT = 1000

DEBUG = False
def debug(msg):
    if DEBUG:
        print(msg)

class Board:
    def __init__(self):
        self.columns = N_COLUMNS
        self.towin = TO_WIN
        self.rows = N_ROWS
        self.board = []
        self.chips_in_column = [0] * self.columns
        for i in range(self.rows):
            self.board.append([BLANK] * self.columns)


    def get_columns(self):
        return self.columns


    def get_rows(self):
        return self.rows


    def clone(self):
        new_board = Board()
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
        for i in range(self.columns):
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
            debug(f"OUT: get_weight: max_depth, player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            return 0

        nb = board.clone()
        ret = nb.play_check_win(player, column)
        if ret == WIN_FOUND:
            weight = (MAX_DEPTH - depth) * player_multiplier * MAJOR_WEIGHT_MULT
            debug(f"OUT: val: {weight},  get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            return weight

        if ret == ERR_COLUMN_FULL:
            return 0

        moves = [MIN_WEIGHT * player_multiplier] * nb.columns
        for i in range(len(moves)):
            moves[i] = self._get_weight(nb, flip_player(player), i, depth+1, max_depth, (-1)*player_multiplier)

        moves = sorted(moves)
        if player_multiplier < 0: 
            first = moves[-1]
            second = moves[-2]
        else:
            first = moves[0]
            second = moves[1]

        if abs(second) == MIN_WEIGHT:
            second = 0
        
        ret = int(first/MAJOR_WEIGHT_MULT)*MAJOR_WEIGHT_MULT + first%MAJOR_WEIGHT_MULT+second
        debug(f"OUT: val: {ret},  get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
        return ret


    def _find_best_move(self, board, player, max_depth):
        moves = [MIN_WEIGHT] * board.columns
        for i in range(len(moves)):
            moves[i] = self._get_weight(board, player, i, 0, max_depth, 1)
        print(f"find_best_move: {moves}")

        m = MIN_WEIGHT * -1
        idx = -1
        for i in range(len(moves)):
            if (not board.is_column_full(i)) and  (moves[i] > m):
                idx = i
                m = moves[i]
        
        return idx 

    def get_best_move(self):
        column = self._find_best_move(self.board, self.player, MAX_DEPTH)
        return column
        

