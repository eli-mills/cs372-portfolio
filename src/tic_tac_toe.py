from typing import Union


class Player:
    """
    Defines data members and methods for a Tic Tac Toe player.
    """
    def __init__(self, player_symbol: str, game) -> None:
        """
        Initializes a Tic Tac Toe player.
        :param player_symbol: X or O
        :param game: associated TicTacToeGame object
        """
        self.SYMBOL = player_symbol
        self.GAME = game

    def pick_square(self, row, col) -> bool:
        """
        Attempts to mark the given square with the player's sign.
        :param row: first level index of game board
        :param col: second level index of game board
        :return: True if successful, else False
        """
        return self.GAME.make_move(self.SYMBOL, row, col)


class TicTacToeGame:
    """
    Defines data members and methods for a game of Tic Tac Toe.
    """
    # CLASS CONSTANTS
    VALIDATION_CODES = [
        "PASSED",
        "WRONG TURN",
        "SPACE OCCUPIED",
        "GAME OVER",
        "INDEX OUT OF RANGE"
    ]

    V_PASSED, V_WRONG_TURN, V_SPACE_OCC, V_GAME_OVER, V_OUT_RANGE = range(5)

    STATUS_CODES = [
        "X TURN",
        "O TURN",
        "X WON",
        "O WON",
        "DRAW",
        "X QUIT",
        "O QUIT"
    ]

    S_X_TURN, S_O_TURN, S_X_WON, S_O_WON, S_DRAW, S_X_QUIT, S_O_QUIT = range(7)

    def __init__(self):
        """
        Initializes a game of Tic Tac Toe with two players.
        """
        self.board = [["_" for _ in range(3)] for _ in range(3)]
        self.players = Player("X", self), Player("O", self)
        self.status = self.S_X_TURN             # Store current game status
        self.validation = self.V_PASSED         # Store last validation result

    def toggle_players(self) -> None:
        """
        Update status to switch to other player.
        """
        self.status = -self.status + 1

    def is_move_valid(self, symbol: str, row: int, col: int) -> bool:
        """
        Checks if the given move is allowed.
        :param symbol: X or O of player making move.
        :param row: first-level index of board to be marked.
        :param col: second-level index of board to be marked.
        :return: True if allowed, otherwise False.
        """
        try:
            # Index corresponds to validation codes
            validations = [
                True,
                symbol == self.players[self.status].SYMBOL,         # WRONG TURN
                self.board[row][col] == "_",                        # OCCUPIED
                self.status < self.S_X_WON                          # GAME OVER
            ]
            if not all(validations):
                self.validation = validations.index(False)
                return False
            self.validation = self.V_PASSED
            return True

        except IndexError:
            self.validation = self.V_OUT_RANGE if self.status < self.S_X_WON \
                else self.V_GAME_OVER
            return False

    def is_win(self) -> bool:
        """
        Check if there is a winning position on the board.
        :return: True if winning position, else False.
        """
        return any([all([square == row[0] != "_" for square in row])    # HOZ _
                    for row in self.board]) \
            or any([all([row[col] == self.board[0][col] != "_"          # VER |
                         for row in self.board]) for col in range(3)]) \
            or all([self.board[idx][idx] == self.board[0][0] != "_"     # DIAG \
                    for idx in range(3)]) \
            or all([self.board[row][col] == self.board[1][1] != "_"     # DIAG /
                    for row in range(3) for col in range(2, -1, -1)
                    if row + col == 2])

    def is_draw(self) -> bool:
        """
        Check if game is in a draw state.
        :return: True if draw, else False.
        """
        return all([square != "_" for row in self.board for square in row])

    def update_is_game_over(self, symbol: str) -> bool:
        """
        Update internal game state if win or draw.
        :param symbol: symbol of current player.
        :return: value of is_game_over
        """
        if self.is_win():
            self.status = {"X": self.S_X_WON, "O": self.S_O_WON}[symbol]
        elif self.is_draw():
            self.status = self.S_DRAW
        return self.status > self.S_O_TURN

    def make_move(self, symbol: str, row: int, col: int) -> bool:
        """
        Marks the given square with the given symbol if allowed.
        :param symbol: X or O of current player.
        :param row: first-level index of board to be marked.
        :param col: second-level index of board to be marked.
        :return: True if successful, else False.
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
        self.status = self.S_X_QUIT if self.status == self.S_X_TURN \
            else self.S_O_QUIT if self.status == self.S_O_TURN \
            else self.status


class TicTacToeCli:
    """
    Provides an API to play a TicTacToeGame via the command line, handling user
    input and printing results.
    """

    def __init__(self):
        self.game = TicTacToeGame()
        self.player, self.opponent = self.game.players
        self.game_requested = False         # Used to coordinate multiplayer
        self.game_confirmed = False         # Used to coordinate multiplayer
        self.is_requesting_party = False

    @staticmethod
    def validate_input(user_move: str) -> Union[tuple[int, int], None]:
        """
        Convert given move string into a move tuple if valid.
        :param user_move: string of expected form "row col".
        :return: converted move (row, col) if valid, else None.
        """
        try:
            row, col = user_move.split(" ")
            return ord(row) - 97, int(col)
        except ValueError:
            return None

    def make_player_move(self, move: str, do_move_as_opp: bool = False) -> bool:
        """
        Makes the given move if valid. Checks game status for end game.
        :param move: expected format "row col".
        :param do_move_as_opp: if True, makes move for opponent player.
        :return: True if move was successful, else False.
        """
        player = self.player if not do_move_as_opp else self.opponent

        # Check if move string in valid format
        converted_move = self.validate_input(move)
        if converted_move is None:
            self.print_board()
            print("Moves must be in the form 'row col'. Try again.")
            return False

        # Check if converted move is legal
        if not player.pick_square(*converted_move):
            self.print_board()
            print(f"Move error: "
                  f"{self.game.VALIDATION_CODES[self.game.validation]}. "
                  f"Try another move.")
            return False

        self.print_board()
        do_move_as_opp and print(f"Player {self.player.SYMBOL}'s turn.")
        self.game.status > TicTacToeGame.S_O_TURN and self.end_game()
        return True

    def request_game(self, is_requestor: bool) -> bool:
        """
        Use when sending a game request to update requestor's state or show
        prompt to requestee.
        :param is_requestor: set True when this is called by the initial player.
                Set False when this is called by the requestee to show prompt.
        :return: True if OK to proceed, else False.
        """
        # Validation
        if self.game_confirmed:
            print("A game is already in progress.")
            return False
        if self.game_requested:
            print("A game is already awaiting confirmation.")
            return False

        # Update state
        self.game_requested = True
        if is_requestor:
            # Person who initiates game is player X
            self.player, self.opponent = self.game.players
            self.is_requesting_party = True
        else:
            # Person who receives game request needs to approve
            print("Play Tic-Tac-Toe? Type /tac to play, /toe to cancel.")
        return True

    def confirm_game(self, is_acceptor: bool) -> bool:
        """
        Use when accepting a game invitation to update acceptor state or show
        prompt to requestor.
        :param is_acceptor: set True when called by message sender, 
            False when called by message receiver.
        :return: True if successful, else False.
        """
        # Validation
        if self.game_confirmed:
            print("A game is already in progress.")
            return False
        if not self.game_requested:
            print("No game to confirm.")
            return False
        if is_acceptor and self.is_requesting_party:
            print("You cannot accept your own invitation!")
            return False

        # Update state
        self.game_confirmed = True
        self.is_requesting_party = False
        if is_acceptor:
            # Person who accepts game request is player O
            self.opponent, self.player = self.game.players
        else:
            # Person who receives confirmation needs to make first move
            self.print_board()
            print("Game accepted. Type your first move, Player X.")
        return True

    def reject_game(self, is_waiting: bool) -> bool:
        """
        Use when rejecting a game invitation to update state of requestor and
        rejector, and to show prompt to requestor.
        :param is_waiting: set True when called by message receiver, 
            False when called by message sender.
        :return: True if successful, else False.
        """
        # Validation
        if self.game_confirmed:
            print("A game is already in progress. Type /q to quit.")
            return False
        if not self.game_requested:
            print("No game to reject.")
            return False
        if not is_waiting and self.is_requesting_party:
            print("You cannot reject your own invitation!")
            return False

        # Update state
        if self.game_requested and self.is_requesting_party:
            print("Your request was rejected.")
        self.is_requesting_party = False
        self.end_game()
        return True

    def end_game(self):
        """
        Reset stored game to a new one and clear flags.
        """
        # Current game wrap-up
        self.game.quit()
        status_message = TicTacToeGame.STATUS_CODES[self.game.status]
        self.game_confirmed and print(f"Game over: {status_message}")

        # Reset state
        self.game = TicTacToeGame()
        self.game_confirmed = False
        self.game_requested = False
        self.is_requesting_party = False

    def print_board(self):
        """
        Prints the current game board to the console.
        """
        row_headings = ['a', 'b', 'c']
        print("\n" * 100)
        # Print column heading
        print("\t" + "\t".join([str(x) for x in range(3)]))

        # Print row headings and cells
        [print(f"{row_headings[idx]}\t" + "\t".join(row))
         for idx, row in enumerate(self.game.board)]
