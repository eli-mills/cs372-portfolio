import socket
from chat_server import ChatSocket, get_args


def main(host, port):
    # Set up socket
    with socket.create_connection((host, port)) as server_socket:
        print(f"Connected to: {host} on port: {port}")
        chatter = ChatSocket(server_socket)

        # Main loop
        while chatter.state != ChatSocket.TERMINATE:
            chatter.chat()


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat client.")
    main(arg_host, arg_port)
