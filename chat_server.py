import socket
import argparse


class ChatSocket:
    CHATTING, PLAYING = range(2)

    def __init__(self, conn_socket):
        self.conn_socket = conn_socket
        self.SOCKET_BUFFER = 1024  # Buffer argument for recv
        self.state = self.CHATTING

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

    @staticmethod
    def parse_for_command(message: str, prints: bool = True) -> bool:
        """
        Checks if message is a command. Returns whether to stop main loop.
        :param message: string to parse
        :param prints: whether to print the message if not a command
        :return: True if need to stop main loop, else False
        """
        if message == "/q":
            return True
        if message == "/tic":
            return False
        prints and print(message)
        return False

    def read_and_print(self):
        message_received = self.read_incoming_data()
        return self.parse_for_command(message_received)

    def send_user_input(self, do_long_prompt):
        do_long_prompt and print("Type /q to quit\nEnter message to send...")
        new_message = input(">")
        self.send_outgoing_data(new_message)
        return self.parse_for_command(new_message, False)


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
            do_long_prompt = True
            chatter = ChatSocket(client_socket)

            # Main loop
            while True:
                if chatter.read_and_print():
                    break
                if chatter.send_user_input(do_long_prompt):
                    break
                do_long_prompt = False


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat server.")
    main(arg_host, arg_port)
