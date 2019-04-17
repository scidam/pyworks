import numpy as np

class TicTacBoard:
    def __init__(self, size=3, state=None, rules={'x': 2, 'o': 1}):
        self.rules = rules
        self.state = np.array(state, dtype=int) if state is not None\
                     else np.zeros((size, size), dtype=int)

    def checker(self, state=None, query='x'):
        '''Simple tictactoe checker.

        Returns `True` if queried gamer  (e.g. `x` or `o`)
        is win.

        #TODO:
            two winners problem needs to be handled... (optionally)
        '''
        state = self.state if state is None else np.array(state, dtype=int)
        if query not in self.rules:
            raise IndexError('Allowed indecies are `x` or `o`.')
        if len(query) != 1:
            raise IndexError('Index length should be equal 1')
        solution = state == self.rules[query]
        return any(np.all(solution, axis=0)) or any(np.all(solution, axis=1)) or\
                all(np.diag(np.fliplr(solution))) or all(np.diag(solution))

    def search_winning_move(self, state=None, query='x'):
        '''Looking for move, that leads to winning.

        Returns (indx, indy) if the move was found or None otherwise.
        '''
        if query not in self.rules:
            raise IndexError('Query value should be declared in rules')
        state = self.state if state is None else np.array(state, dtype=int)
        allowed_positions = ~((state == self.rules['x']) |
                              (state == self.rules['o']))
        if not allowed_positions.any():
            return None
        for ir, ic in zip(*np.where(allowed_positions)):
            _state = state.copy()
            _state[ir, ic] = self.rules[query]
            if self.checker(_state, query=query):
                    return ir, ic
        return None

    def suggest_move(self, query='x'):
        '''Try to suggest move, that your opponent wouldn't win by next move.
        '''
        if query not in self.rules:
            raise IndexError('Query value should be declared in rules')
        allowed_positions = ~((self.state == self.rules['x']) |
                              (self.state == self.rules['o']))
        if not allowed_positions.any():
            # No moves available
            # raise custom exception here or print error msg...
            return None
        else:

           # Searching for winning position
            prob_res = self.search_winning_move(query=query)
            if prob_res:
                print('You will win, if accept the move...')
                return prob_res

            #No winning moves were found
            for ir, ic in zip(*np.where(allowed_positions)):
                _state = self.state.copy()
                _state[ir, ic] = self.rules[query]
                if self.search_winning_move(_state,
                                            query='x' if query == 'o' else 'o') is None:
                    return ir, ic
            print('Sorry...your opponent will win in any case...')
            return None

# ---------- testing ----------------
# 2 = x
# 1 = o
# 0 = Empty

nowin = np.array([[0, 1, 2], [1,1,0], [2,2,1]])
board = TicTacBoard(state=nowin)
print('nowin: checking for winner `x`, result=', board.checker( query='x'))
print('nowin: checking for winner `o`, result=', board.checker(query='o'))


winx = np.array([[0, 1, 2], [1,2,0], [2,0,1]])
print('winx: checking for winner `x`, result=', board.checker(winx, query='x'))
print('winx: checking for winner `o`, result=', board.checker(winx, query='o'))

# -------------------------------------



# --------- more complicated ... ------

test_board = np.zeros((3,3), dtype=int)
test_board[2,2] = 1
test_board[2,1] = 1
test_board[1,2] = 1
test_board[1,1] = 2

#  |   |
#---------
#  | x | o
#---------
#  | o | o

board = TicTacBoard(state=test_board)

# Suggest move for 'x' (default)
suggested = board.suggest_move()
print('Hint for x: ', suggested)

# Suggest move for 'o':
suggested = board.suggest_move(query='o')
print('Hint for o:', suggested)

# ----- another case --
test_board = np.zeros((3,3), dtype=int)
test_board[2,2] = 1
test_board[2,1] = 1
test_board[1,1] = 2

#  |   |
#---------
#  | x |
#---------
#  | o | o
#----------------------

board = TicTacBoard(state=test_board)
result = board.suggest_move()
print('Try this move: ', result)

