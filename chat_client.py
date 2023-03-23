import socket
from chat_server import get_args
from chat_interface import ChatInterface


def main(host, port):
    # Set up socket
    with socket.create_connection((host, port)) as server_socket:
        print(f"Connected to: {host} on port: {port}")
        chatter = ChatInterface(server_socket)

        # Main loop
        while chatter.state != ChatInterface.TERMINATE:
            chatter.chat()


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat client.")
    main(arg_host, arg_port)
