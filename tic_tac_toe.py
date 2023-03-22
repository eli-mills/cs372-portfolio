import os


class Player:
    """
    Defines data members and methods for a Tic Tac Toe player.
    """
    def __init__(self, player_symbol, game) -> None:
        """
        Initializes a Tic Tac Toe player.
        """
        self.SYMBOL = player_symbol
        self.GAME = game
        self.is_my_turn = False

    def toggle_turn(self):
        """
        Sets is_my_turn to opposite value.
        """
        self.is_my_turn = not self.is_my_turn

    def pick_square(self, row, col) -> bool:
        """
        Attempts to mark the given square with the player's sign.
        :param row: first level index of game board
        :param col: second level index of game board
        :return: True if successful, else False
        """
        return (self.is_my_turn
                and self.GAME.make_move(self.SYMBOL, row, col) or print("Move failed validation. Try again.")) \
            or print("Current player is not active.")


class TicTacToeGame:
    """
    Defines data members and methods for a game of Tic Tac Toe.
    """
    def __init__(self):
        """
        Initializes a game of Tic Tac Toe with two players.
        """
        self.board = [["_" for _ in range(3)] for _ in range(3)]
        self.players = Player("X", self), Player("O", self)
        self.players[0].is_my_turn = True
        self.is_game_over = False

    def toggle_players(self) -> None:
        """
        Switch each player's active state and update current player.
        """
        [player.toggle_turn() for player in self.players]

    def is_move_valid(self, row: int, col: int) -> bool:
        """
        Checks if the given move is allowed. Assumes active player is making move.
        :param row: first-level index of board
        :param col: second-level index of board
        :return: True if allowed, otherwise False.
        """
        try:
            return (self.board[row][col] == "_" or print("Move failed: space not available."))\
                and (not self.is_game_over or print("Move failed: game is over."))
        except IndexError:
            print("Index out of range.")
            return False

    def is_win(self) -> bool:
        """
        Check if there is a winning position on the board.
        :return: True if winning position, else False.
        """
        return any([all([square == row[0] != "_" for square in row]) for row in self.board]) \
            or any([all([row[col] == self.board[0][col] != "_" for row in self.board]) for col in range(3)]) \
            or all([self.board[idx][idx] == self.board[0][0] != "_" for idx in range(3)]) \
            or all([self.board[row][col] == self.board[1][1] != "_" for row in range(3) for col in range(2, -1, -1)])

    def is_draw(self) -> bool:
        """
        Check if game is in a draw state.
        :return: True if draw, else False.
        """
        return all([square != "_" for row in self.board for square in row])

    def update_is_game_over(self, symbol) -> bool:
        """
        Check for game over state. Print message and update internal state.
        :param symbol: symbol of current turn.
        :return: value of is_game_over
        """
        if self.is_win():
            print(f"Game over: {symbol}'s win!")
            self.is_game_over = True
        elif self.is_draw():
            print("Game over: draw.")
            self.is_game_over = True
        return self.is_game_over

    def print_board(self):
        """
        Prints the current game board to the console.
        """
        print("\t" + "\t".join([str(x) for x in range(3)]))
        [print(f"{idx}\t" + "\t".join(row)) for idx, row in enumerate(self.board)]

    def make_move(self, symbol: str, row: int, col: int) -> bool:
        """
        Marks the given square with the given symbol if allowed.
        :param symbol: X or O
        :param row: first-level index of board
        :param col: second-level index of board
        :return: True if successful, else False
        """
        if not self.is_move_valid(row, col):
            return False
        self.board[row][col] = symbol
        self.update_is_game_over(symbol) and self.toggle_players()
        self.print_board()
        return True
