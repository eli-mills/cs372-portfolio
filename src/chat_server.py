import socket
import argparse
from chat_interface import ChatInterface


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

    # Manage connection
    with client_socket:
        print(f"Connected by {addr}")
        print("Waiting for message...")
        chatter = ChatInterface(client_socket, True)
        while chatter.state != ChatInterface.TERMINATE:
            chatter.chat()


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat server.")
    main(arg_host, arg_port)
