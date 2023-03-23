from tic_tac_toe import TicTacToeCli
from typing import Union


class ChatInterface:
    CHATTING, WAITING, TERMINATE = range(3)  # Status codes
    SOCKET_BUFFER = 1024  # Buffer argument for recv
    DELIMITER = '\0'  # Use to sep length and data

    def __init__(self, conn_socket, is_server=False):
        self.conn_socket = conn_socket
        self.state = self.WAITING if is_server else self.CHATTING
        self.do_long_prompt = True
        self.cli = TicTacToeCli()

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

    def parse_for_command(self, message: str) -> Union[str, None]:
        """
        Checks if message is a command. Executes command accordingly.
        Updates internal state if terminating.
        :param message: string to parse
        :return: None if message is not parsable, else message to send.
        """
        # Control messages
        if message == "/q":
            if self.cli.game_confirmed:
                self.cli.end_game()
                return message
            self.state = self.TERMINATE
            return message
        if message == "/tic":
            return message if self.cli.request_game(
                self.state == self.CHATTING) else None
        if message == "/tac":
            return message if self.cli.confirm_game(
                self.state == self.CHATTING) else None
        if message == "/toe":
            return message if self.cli.reject_game(
                self.state == self.WAITING) else None

        # String messages
        if self.cli.game_confirmed:
            return message if self.cli.make_player_move(message,
                                                        self.state == self.WAITING) else None

        self.state == self.WAITING and print(message)
        return message

    def receive_and_handle_message(self) -> bool:
        """
        Handle incoming message from socket.
        :return: True if message should break main loop, else False.
        """
        message_received = self.read_incoming_data()
        self.parse_for_command(message_received)
        self.state = self.CHATTING if self.state == self.WAITING else self.state

    def send_and_handle_user_input(self):
        """
        Prompt for user input until acceptable input received. Updates state.
        """
        self.do_long_prompt and print(
            "Type /q to quit\nEnter message to send...")
        self.do_long_prompt = False

        # Loop until parsable input is returned
        while True:
            new_message = self.parse_for_command(input(">"))
            if new_message is not None:
                break

        self.send_outgoing_data(new_message)
        self.state = self.WAITING if self.state == self.CHATTING else self.state

    def chat(self):
        """
        Waits for incoming message or sends new message depending on state.
        """
        if self.state == self.CHATTING:
            self.send_and_handle_user_input()
        elif self.state == self.WAITING:
            self.receive_and_handle_message()
        else:
            print("Chat Interface is unavailable.")
            return None
