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
ERR_STACK_EMPTY = 4
WIN_FOUND = 5
WIN_NOT_FOUND = 6


MAX_DEPTH = TO_WIN + 2
MIN_WEIGHT = 100000

DEBUG = False
def debug(msg):
    if DEBUG:
        sys.stderr.write(msg)
        sys.stderr.write("\n")

class Board:
    def __init__(self):
        self.columns = N_COLUMNS
        self.towin = TO_WIN
        self.rows = N_ROWS
        self.board = []
        self.chips_in_column = [0] * self.columns
        self.move_stack = []
        for i in range(self.rows):
            self.board.append([BLANK] * self.columns)
        self.positive_diag = []
        for i in range(self.rows):
            self.positive_diag.append([None] * self.columns)
        self.negative_diag = []
        for i in range(self.rows):
            self.negative_diag.append([None] * self.columns)
        self._calculate_diags()

    def _calculate_diags(self):
        # Positive
        for i in range(self.columns):
            points = []
            cr = 0
            for j in range(0, min(self.columns-i, self.rows)):
                points.append([cr, i+j])
                cr += 1
            if len(points) >= self.towin:
                for point in points:
                    self.positive_diag[point[0]][point[1]] = points

        for i in range(self.rows):
            points = []
            cc = 0
            for j in range(0, min([self.rows-i, self.columns])):
                points.append([i+j, cc])
                cc += 1
            if len(points) >= self.towin:
                for point in points:
                    self.positive_diag[point[0]][point[1]] = points

        # Negative
        for i in range(self.columns):
            points = []
            cr = 0
            for j in range(0, min([i, self.rows])):
                points.append([cr, i-j])
                cr += 1
            if len(points) >= self.towin:
                for point in points:
                    self.negative_diag[point[0]][point[1]] = points

        for i in range(self.rows):
            points = []
            cc = self.columns-1
            for j in range(0, min([self.rows-i, self.columns])):
                points.append([i+j, cc])
                cc -= 1
            if len(points) >= self.towin:
                for point in points:
                    self.negative_diag[point[0]][point[1]] = points

    def get_columns(self):
        return self.columns


    def get_rows(self):
        return self.rows

    def play(self, player, column):
        if self.columns <= column:
            return ERR_INVALID_COLUMN

        if self.chips_in_column[column] == self.rows:
            return ERR_COLUMN_FULL

        self.board[self.chips_in_column[column]][column] = player
        self.chips_in_column[column] += 1
        self.move_stack.append(column)
        return SUCCESS

    def undo(self):
        if len(self.move_stack) == 0:
            return ERR_STACK_EMPTY

        column = self.move_stack.pop(-1)
        self.board[self.chips_in_column[column]-1][column] = BLANK
        self.chips_in_column[column] -= 1
        return SUCCESS


    def _check_column_win(self, player, column):
        if self.chips_in_column[column] < self.towin:
            return WIN_NOT_FOUND

        seq = 0
        for i in range(self.chips_in_column[column]):
            '''
            if self.chips_in_column[i] - i + seq < self.towin:
                return WIN_NOT_FOUND
            '''

            if self.board[i][column] == player:
                seq += 1
                if seq == self.towin:
                    return WIN_FOUND
            else:
                seq = 0
        return WIN_NOT_FOUND


    def _check_row_win(self, player, column):
        seq = 0
        row = self.chips_in_column[column] - 1
        for c in range(self.columns):
            '''
            if self.columns - c + seq < self.towin:
                return WIN_NOT_FOUND
            '''
            if self.board[row][c] == player:
                seq += 1
                if seq == self.towin:
                    return WIN_FOUND
            else:
                seq = 0
        return WIN_NOT_FOUND

    def _check_one_diag(self, player, diag, row, column):
        if diag[row][column]:
            seq = 0
            for point in diag[row][column]:
                if self.board[point[0]][point[1]] == player:
                    seq += 1
                    if seq == self.towin:
                        return WIN_FOUND
                else:
                    seq = 0

    def _check_diag_win(self, player, column):
        row = self.chips_in_column[column]-1
        if self._check_one_diag(player, self.positive_diag, row, column) == WIN_FOUND:
            return WIN_FOUND
        if self._check_one_diag(player, self.negative_diag, row, column) == WIN_FOUND:
            return WIN_FOUND
        return WIN_NOT_FOUND


    def play_check_win(self, player, column):
        p = self.play(player, column)
        if p != SUCCESS:
            return p
        if self._check_column_win(player, column) == WIN_FOUND:
            return WIN_FOUND

        if self._check_row_win(player, column) == WIN_FOUND:
            return WIN_FOUND

        if self._check_diag_win(player, column) == WIN_FOUND:
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

    def print_board(self, outstream=sys.stdout):
        if not DEBUG and outstream == sys.stderr:
            return

        for r in range(self.rows-1, -1, -1):
            for c in self.board[r]:
                outstream.write(f"{PLAYER_TEXT[c]} ")
            outstream.write("\n")
        for i in range(self.columns):
            outstream.write(f"{i} ")
        outstream.write("\n")
        outstream.write("======================\n")


def flip_player(player):
    return PLAYER_2 if player == PLAYER_1 else PLAYER_1

class Connect4Engine:
    def __init__(self, board, player):
        self.board = board
        self.player = player

    def _get_weight(self, board, player, column, depth, max_depth, player_multiplier):
        if depth > MAX_DEPTH:
            #debug(f"IN: get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            #debug(f"OUT: get_weight: max_depth, player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            #debug("-------------------")
            return 0

        ret = board.play_check_win(player, column)
        if ret == WIN_FOUND:
            weight = (MAX_DEPTH - depth) * player_multiplier
            debug(f"IN: get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            board.print_board(outstream=sys.stderr)
            debug(f"OUT: val: {weight},  get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
            debug("-------------------")
            board.undo()
            return weight

        if ret == ERR_COLUMN_FULL:
            return MIN_WEIGHT * player_multiplier * -1

        moves = [MIN_WEIGHT * player_multiplier] * board.columns
        for i in range(board.columns):
            if not board.is_column_full(i):
                moves[i] = self._get_weight(board, flip_player(player), i, depth+1, max_depth, (-1)*player_multiplier)

        if player_multiplier < 0: 
            ret = max(moves)
        else:
            ret = min(moves)

        ret = ret
        debug(f"IN: get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
        board.print_board(outstream=sys.stderr)
        debug(f"moves: {moves}")
        debug(f"OUT: val: {ret},  get_weight: player: {PLAYER_TEXT[player]}, col: {column}, depth: {depth}, pm: {player_multiplier}")
        debug("-------------------")

        board.undo()
        return ret


    def _find_best_move(self, board, player, max_depth):
        moves = [MIN_WEIGHT] * board.columns
        for i in range(len(moves)):
            moves[i] = self._get_weight(board, player, i, 0, max_depth, 1)
        print(f"find_best_move: {moves}")

        m = MIN_WEIGHT * -1
        next_moves = []
        for i in range(len(moves)):
            if board.is_column_full(i):
                continue
            if moves[i] > m:
                next_moves = [i]
                m = moves[i]
            elif moves[i] == m:
                next_moves.append(i)
        
        return next_moves[random.randint(0, len(next_moves)-1)]

    def get_best_move(self):
        column = self._find_best_move(self.board, self.player, MAX_DEPTH)
        return column
        


class BoardHistory:
    def __init__(self):
        self.boards = []

    def push(self, board):
        self.boards.append(board.clone())

    def print_history(self):
        for board in self.boards:
            board.print_board()

