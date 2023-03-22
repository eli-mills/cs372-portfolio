import socket
import argparse
import tic_tac_toe


class ChatSocket:
    CHATTING, WAITING, TERMINATE = range(3)

    def __init__(self, conn_socket, is_server=False):
        self.conn_socket = conn_socket
        self.SOCKET_BUFFER = 1024  # Buffer argument for recv
        self.state = self.WAITING if is_server else self.CHATTING
        self.do_long_prompt = True
        self.game = None

    @staticmethod
    def parse_socket_data(socket_content: str) -> list[str]:
        """
        Parses a string for length and data.
        :param socket_content: string received from socket
        :return: tuple containing length (int) and data chunk (string)
        """
        if socket_content[0] != ":":
            raise ValueError("read_incoming_data: missing valid start token")
        return socket_content.split(":")[1:]

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
        str_msg = f":{len(msg_to_send)}:{msg_to_send}"
        byte_msg = str_msg.encode()

        # Send data
        total_bytes = 0
        while total_bytes < len(byte_msg):
            total_bytes += self.conn_socket.send(byte_msg[total_bytes:])

    def make_player_move(self, move):
        pass

    def start_game(self):
        self.game = tic_tac_toe.TicTacToeGame()

    def parse_for_command(self, message: str, prints: bool = True) -> None:
        """
        Checks if message is a command. Returns whether to stop main loop.
        :param message: string to parse
        :param prints: whether to print the message if not a command
        """
        if message == "/q":
            self.state = self.TERMINATE
            return
        if message == "/tic":
            pass
        prints and print(message)

    def read_and_handle(self) -> bool:
        """
        Handle incoming message from socket.
        :return: True if message should break main loop, else False.
        """
        message_received = self.read_incoming_data()
        self.state = self.CHATTING
        self.parse_for_command(message_received)

    def send_user_input(self):
        self.do_long_prompt and print("Type /q to quit\nEnter message to send...")
        new_message = input(">")
        self.send_outgoing_data(new_message)
        self.state = self.WAITING
        self.parse_for_command(new_message, False)
        self.do_long_prompt = False

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
            chatter = ChatSocket(client_socket, True)

            # Main loop
            while chatter.state != ChatSocket.TERMINATE:
                chatter.chat()


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat server.")
    main(arg_host, arg_port)
