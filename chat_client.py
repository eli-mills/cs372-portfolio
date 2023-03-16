import socket
from chat_server import read_incoming_data, send_outgoing_data, get_args


def main(host, port):
    with socket.create_connection((host, port)) as server_socket:
        print(f"Connected to: {host} on port: {port}")
        print("Type /q to quit")
        print("Enter message to send...")
        while True:
            new_message = input(">")
            send_outgoing_data(server_socket, new_message)
            if new_message == "/q":
                break
            message_received = read_incoming_data(server_socket)
            if not message_received:
                continue
            if message_received == "/q":
                break
            print(message_received)


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat client.")
    main(arg_host, arg_port)
