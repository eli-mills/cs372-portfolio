import socket
from chat_server import read_incoming_data, send_outgoing_data


def main():
    with socket.create_connection(("localhost", 8080)) as server_socket:
        print("Connected to: localhost on port: 8080")
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
    main()
