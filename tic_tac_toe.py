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
        # if not self.is_my_turn:
        #     print(f"Player {self.SYMBOL}: it is not your turn.")
        #     return False

        return self.GAME.make_move(self.SYMBOL, row, col) \
            or print("Move failed validation. Try again.")


class TicTacToeGame:
    """
    Defines data members and methods for a game of Tic Tac Toe.
    """
    VALIDATION_CODES = [
        "PASSED",
        "WRONG TURN",
        "SPACE OCCUPIED",
        "GAME OVER",
        "INDEX OUT OF RANGE"
    ]

    STATUS_CODES = [
        "X TURN",
        "O TURN",
        "X WON",
        "O WON",
        "DRAW"
    ]

    def __init__(self):
        """
        Initializes a game of Tic Tac Toe with two players.
        """
        self.board = [["_" for _ in range(3)] for _ in range(3)]
        self.players = Player("X", self), Player("O", self)
        self.status = 0
        self.validation = 0

    def toggle_players(self) -> None:
        """
        Switch each player's active state and update current player.
        """
        self.status = -self.status + 1

    def is_move_valid(self, symbol: str, row: int, col: int) -> bool:
        """
        Checks if the given move is allowed. Assumes active player is making move.
        :param symbol: X or O
        :param row: first-level index of board
        :param col: second-level index of board
        :return: True if allowed, otherwise False.
        """
        try:
            validations = [
                True,
                symbol == self.players[self.status].SYMBOL,         # WRONG TURN
                self.board[row][col] == "_",                        # OCCUPIED
                self.status < 2                                     # GAME OVER
            ]
            if not all(validations):
                self.validation = validations.index(False)
                return False
            self.validation = 0
            return True
        except IndexError:                          # INDEX OUT OF RANGE
            self.validation = 4 if self.status < 2 else 3
            return False

    def is_win(self) -> bool:
        """
        Check if there is a winning position on the board.
        :return: True if winning position, else False.
        """
        return any([all([square == row[0] != "_" for square in row])
                    for row in self.board]) \
            or any([all([row[col] == self.board[0][col] != "_"
                         for row in self.board]) for col in range(3)]) \
            or all([self.board[idx][idx] == self.board[0][0] != "_"
                    for idx in range(3)]) \
            or all([self.board[row][col] == self.board[1][1] != "_"
                    for row in range(3) for col in range(2, -1, -1)])

    def is_draw(self) -> bool:
        """
        Check if game is in a draw state.
        :return: True if draw, else False.
        """
        return all([square != "_" for row in self.board for square in row])

    def update_is_game_over(self, symbol) -> bool:
        """
        Update internal game state if win or draw.
        :param symbol: symbol of current turn.
        :return: value of is_game_over
        """
        if self.is_win():
            self.status = ["X", "O"].index(symbol) + 2
        elif self.is_draw():
            self.status = 4
        return self.status > 1

    def print_board(self):
        """
        Prints the current game board to the console.
        """
        print("\t" + "\t".join([str(x) for x in range(3)]))
        [print(f"{idx}\t" + "\t".join(row))
         for idx, row in enumerate(self.board)]

    def make_move(self, symbol: str, row: int, col: int) -> bool:
        """
        Marks the given square with the given symbol if allowed.
        :param symbol: X or O
        :param row: first-level index of board
        :param col: second-level index of board
        :return: True if successful, else False
        """
        if not self.is_move_valid(symbol, row, col):
            return False
        self.board[row][col] = symbol
        not self.update_is_game_over(symbol) and self.toggle_players()
        return True


def tic_tac_toe_cli():
    pass


if __name__ == '__main__':
    new_game = TicTacToeGame()
    player_x, player_o = new_game.players
    move_list = [
        (player_x, (0, 0)),
        (player_x, (0, 1)),         # Wrong turn
        (player_o, (0, 1)),
        (player_x, (10, 10)),       # Out of range
        (player_x, (0, 0)),         # Occupied space
        (player_x, (1, 0)),
        (player_o, (1, 1)),
        (player_x, (2, 0)),         # Player X wins
        (player_x, (2, 2)),         # Game is over
        (player_o, (2, 2))          # Wrong turn
    ]
    for player, move in move_list:
        player.pick_square(*move)
        print(TicTacToeGame.VALIDATION_CODES[new_game.validation])
        print(TicTacToeGame.STATUS_CODES[new_game.status])
        new_game.print_board()
