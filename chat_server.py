import socket
import argparse
import tic_tac_toe


class ChatInterface:
    CHATTING, WAITING, TERMINATE = range(3)         # Status codes
    SOCKET_BUFFER = 1024                        # Buffer argument for recv
    DELIMITER = '\0'

    def __init__(self, conn_socket, is_server=False):
        self.conn_socket = conn_socket
        self.state = self.WAITING if is_server else self.CHATTING
        self.do_long_prompt = True
        self.game, self.player, self.opponent = None, None, None
        self.game_confirmed = False

    @staticmethod
    def parse_socket_data(socket_content: str) -> list[str]:
        """
        Parses a string for length and data.
        :param socket_content: string received from socket
        :return: list of strings containing length and data chunk
        """
        if socket_content[0] != ChatInterface.DELIMITER:
            raise ValueError("read_incoming_data: missing valid start token")
        return socket_content.split(ChatInterface.DELIMITER)[1:]

    def read_incoming_data(self):
        # Receive data length
        socket_content = self.conn_socket.recv(self.SOCKET_BUFFER).decode()
        if not socket_content:
            return

        while len(self.parse_socket_data(socket_content)) < 2:
            socket_content += self.conn_socket.recv(self.SOCKET_BUFFER).decode()

        length, data = self.parse_socket_data(socket_content)

        # Receive rest of data
        while len(data) < int(length):
            data += self.conn_socket.recv(self.SOCKET_BUFFER).decode()

        return data.strip()

    def send_outgoing_data(self, msg_to_send):
        # Format and package data
        str_msg = self.DELIMITER.join(["", str(len(msg_to_send)), msg_to_send])
        byte_msg = str_msg.encode()

        # Send data
        total_bytes = 0
        while total_bytes < len(byte_msg):
            total_bytes += self.conn_socket.send(byte_msg[total_bytes:])

    def make_player_move(self, move):
        player = self.player if self.state == self.CHATTING else self.opponent
        valid_move = self.game.validate_input(move)
        while not player.pick_square(*valid_move):
            print(f"Move error: "
                  f"{self.game.VALIDATION_CODES[self.game.validation]}. "
                  f"Try another move.")
            valid_move = self.game.validate_input(input(">"))
            self.game.print_board()
        self.game.print_board()
        self.game.status > 1 and self.end_game()
        return f"{valid_move[0]} {valid_move[1]}"

    def start_game(self):
        if self.game is not None:
            return

        # Person who initiates game is player X
        if self.state == self.CHATTING:
            self.game = tic_tac_toe.TicTacToeGame()
            self.player, self.opponent = self.game.players
        else:
            # Person who receives game request needs to approve
            print("Play Tic-Tac-Toe? Type /tac to play, /toe to cancel.")

    def confirm_game(self):
        self.game_confirmed = True

        # Acceptor needs to set up game
        if self.state == self.CHATTING:
            self.game = tic_tac_toe.TicTacToeGame()
            self.opponent, self.player = self.game.players
        else:
            # Person who receives request needs to make first move
            print("Game accepted. Type your first move.")
            self.game.print_board()

    def end_game(self):
        self.game_confirmed and print(f"Game over: "
                            f"{tic_tac_toe.TicTacToeGame.STATUS_CODES[self.game.status]}")
        self.game = None
        self.game_confirmed = False

    def parse_for_command(self, message: str) -> str:
        """
        Checks if message is a command. Updates internal state if terminating.
        :param message: string to parse
        """
        prints = self.state == self.WAITING
        # Commands to parse regardless of state
        if message == "/q":
            self.state = self.TERMINATE
            return
        if message == "/tic":               # Initiate game request
            self.start_game()
            prints = False
        elif message == "/tac":               # Accept game request
            self.confirm_game()
            prints = False
        elif message == "/toe":               # Reject game request
            self.end_game()
            self.state == self.WAITING and print("Your request was rejected.")
            prints = False
        # Commands with behavior determined by state
        elif self.game_confirmed:
            message = self.make_player_move(message)   # Return valid move

        prints and print(message)
        return message

    def read_and_handle(self) -> bool:
        """
        Handle incoming message from socket.
        :return: True if message should break main loop, else False.
        """
        message_received = self.read_incoming_data()
        self.parse_for_command(message_received)
        self.state = self.CHATTING if self.state == self.WAITING else self.state

    def send_user_input(self):
        self.do_long_prompt and print("Type /q to quit\nEnter message to send...")
        self.do_long_prompt = False
        new_message = input(">")
        new_message = self.parse_for_command(new_message)
        self.send_outgoing_data(new_message)
        self.state = self.WAITING if self.state == self.CHATTING else self.state

    def chat(self):
        """
        Waits for incoming message or sends new message depending on state.
        """
        if self.state == self.CHATTING:
            self.send_user_input()
        elif self.state == self.WAITING:
            self.read_and_handle()


def get_args(desc=""):
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-ip", "--ip-address", type=str, default="localhost",
                        help="host address")
    parser.add_argument("-p", "--port-number", type=int, default=8080,
                        help="port number")
    args = parser.parse_args()
    return args.ip_address, args.port_number


def main(host, port):
    # Set up socket
    with socket.create_server((host, port)) as server_socket:
        print(f"Server listening on: {host} on port: {port}")
        client_socket, addr = server_socket.accept()
        with client_socket:
            print(f"Connected by {addr}")
            print("Waiting for message...")
            chatter = ChatInterface(client_socket, True)

            # Main loop
            while chatter.state != ChatInterface.TERMINATE:
                chatter.chat()


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat server.")
    main(arg_host, arg_port)
