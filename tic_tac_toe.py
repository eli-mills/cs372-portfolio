from typing import Union


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

        return self.GAME.make_move(self.SYMBOL, row, col)


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

    PASSED, WRONG_TURN, SPACE_OCCUPIED, GAME_OVER, INDEX_OUT_OF_RANGE = range(5)

    STATUS_CODES = [
        "X TURN",
        "O TURN",
        "X WON",
        "O WON",
        "DRAW",
        "X QUIT",
        "O QUIT"
    ]

    X_TURN, O_TURN, X_WON, O_WON, DRAW, X_QUIT, O_QUIT = range(7)

    def __init__(self):
        """
        Initializes a game of Tic Tac Toe with two players.
        """
        self.board = [["_" for _ in range(3)] for _ in range(3)]
        self.players = Player("X", self), Player("O", self)
        self.status = 0
        self.validation = 0

    @staticmethod
    def validate_input(user_move: str) -> Union[tuple[int, int], None]:
        """
        Convert given move string into a move tuple if valid.
        :param user_move: string of expected form row col
        :return: converted move if valid, else None
        """
        try:
            row, col = user_move.split(" ")
            row, col = int(row), int(col)
            return row, col
        except ValueError:
            print("Moves must be in the form 'row col'. Try again.")
            return None

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
                    for row in range(3) for col in range(2, -1, -1)
                    if row + col == 2])

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

    def quit(self):
        """
        Update internal state if game quits on a player's turn.
        """
        self.status = self.X_QUIT if self.status == self.X_TURN \
            else self.O_QUIT if self.status == self.O_TURN \
            else self.status


class TicTacToeCli:
    """
    Provides an API to play a TicTacToeGame via the command line, handling user
    input and print statements.
    """
    def __init__(self, do_go_first=True):
        self.game = TicTacToeGame()
        self.player, self.opponent = self.game.players if do_go_first else self.game.players[::-1]
        self.game_requested = False
        self.game_confirmed = False

    @staticmethod
    def validate_input(user_move: str) -> Union[tuple[int, int], None]:
        """
        Convert given move string into a move tuple if valid.
        :param user_move: string of expected form row col
        :return: converted move if valid, else None
        """
        try:
            row, col = user_move.split(" ")
            row, col = int(row), int(col)
            return row, col
        except ValueError:
            print("Moves must be in the form 'row col'. Try again.")
            return None

    def make_player_move(self, move: str, do_move_as_opp: bool = False) -> bool:
        """
        Makes the given move if valid.
        :param move: expected format row col
        :param do_move_as_opp: if True, makes move for opponent player
        :return: True if move was successful, else False
        """
        player = self.player if not do_move_as_opp else self.opponent
        valid_move = self.validate_input(move)
        if valid_move is None:
            return False
        if not player.pick_square(*valid_move):
            self.print_board()
            print(f"Move error: "
                  f"{self.game.VALIDATION_CODES[self.game.validation]}. "
                  f"Try another move.")
            return False
        self.print_board()
        self.game.status > 1 and self.end_game()
        return True

    def request_game(self, is_requestor: bool) -> bool:
        """
        Use to confirm whether to proceed with sending a game request.
        :return: True if GO to proceed, else False.
        """
        if self.game_confirmed:
            print("A game is already in progress.")
            return False

        if self.game_requested:
            print("A game is already awaiting confirmation.")
            return False

        self.game_requested = True
        # Person who initiates game is player X
        if is_requestor:
            self.player, self.opponent = self.game.players
        else:
            # Person who receives game request needs to approve
            print("Play Tic-Tac-Toe? Type /tac to play, /toe to cancel.")
        return True

    def confirm_game(self, is_acceptor: bool) -> bool:
        """
        Updates internal state to confirm game.
        :return: True if successful, else False.
        """
        # Validation
        if self.game_confirmed:
            print("A game is already in progress.")
            return False

        if not self.game_requested:
            print("No game to confirm.")
            return False

        self.game_confirmed = True

        # Acceptor needs to set up game
        if is_acceptor:
            self.opponent, self.player = self.game.players
        else:
            # Person who receives confirmation needs to make first move
            print("Game accepted. Type your first move.")
            self.print_board()
        return True

    def reject_game(self, is_waiting: bool) -> bool:
        """
        Rejects a requested game if request was made.
        :return: True if successful, else False.
        """
        if self.game_confirmed:
            print("A game is already in progress. Type /q to quit.")
            return False

        if not self.game_requested:
            print("No game to reject.")
            return False

        if self.game_requested and is_waiting:
            print("Your request was rejected.")
        self.end_game()
        return True

    def end_game(self):
        self.game.quit()
        status_message = TicTacToeGame.STATUS_CODES[self.game.status]
        self.game_confirmed and print(f"Game over: {status_message}")
        self.game = TicTacToeGame()
        self.game_confirmed = False
        self.game_requested = False

    def print_board(self):
        """
        Prints the current game board to the console.
        """
        print("\t" + "\t".join([str(x) for x in range(3)]))
        [print(f"{idx}\t" + "\t".join(row))
         for idx, row in enumerate(self.game.board)]
