import socket
import argparse


SOCKET_BUFFER = 1024        # Buffer argument for recv

def parse_socket_data(socket_content: str) -> list[str]:
    """
    Parses a string for length and data.
    :param socket_content: string received from socket
    :return: tuple containing length (int) and data chunk (string)
    """
    if socket_content[0] != ":":
        raise ValueError("read_incoming_data: missing valid start token")
    return socket_content.split(":")[1:]


def read_incoming_data(client_socket):
    # Receive data length
    socket_content = client_socket.recv(SOCKET_BUFFER).decode()
    if not socket_content:
        return

    while len(parse_socket_data(socket_content)) < 2:
        socket_content += client_socket.recv(SOCKET_BUFFER).decode()

    length, data = parse_socket_data(socket_content)

    # Receive rest of data
    while len(data) < int(length):
        data += client_socket.recv(SOCKET_BUFFER).decode()

    return data.strip()


def send_outgoing_data(client_socket, msg_to_send):
    # Format and package data
    str_msg = f":{len(msg_to_send)}:{msg_to_send}"
    byte_msg = str_msg.encode()

    # Send data
    total_bytes = 0
    while total_bytes < len(byte_msg):
        total_bytes += client_socket.send(byte_msg[total_bytes:])


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
        server_socket.listen(5)
        print(f"Server listening on: {host} on port: {port}")
        client_socket, addr = server_socket.accept()
        with client_socket:
            print(f"Connected by {addr}")
            print("Waiting for message...")
            do_long_prompt = True
            long_prompt = "Type /q to quit\nEnter message to send..."
            # Main loop
            while True:
                message_received = read_incoming_data(client_socket)
                if message_received == "/q":
                    break
                print(message_received)
                do_long_prompt and print(long_prompt)
                do_long_prompt = False
                new_message = input(">")
                send_outgoing_data(client_socket, new_message)
                if new_message == "/q":
                    break


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat server.")
    main(arg_host, arg_port)
