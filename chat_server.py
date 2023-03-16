import socket


def read_incoming_data(client_socket):
    # 1. Receive data length
    socket_content = client_socket.recv(1024).decode()
    if not socket_content:
        return ""
    if socket_content[0] != ":":
        raise ValueError("read_incoming_data: missing valid start token")
    content_split = socket_content.split(":")[1:]
    while len(content_split) < 2:
        new_split = client_socket.recv(1024).decode().split(":")
        content_split[0] += new_split[0]
        len(new_split) > 1 and content_split.append(new_split[1])
    length, data = content_split

    # 2. Receive rest of data
    while len(data) < int(length):
        data += client_socket.recv(1024).decode()

    # 3. Result
    return data.strip()


def send_outgoing_data(client_socket, msg_to_send):
    # 1. Format and package data
    str_msg = f":{len(msg_to_send)}:{msg_to_send}"
    byte_msg = str_msg.encode()

    # 2. Send data
    client_socket.send(byte_msg)
    return


def main():
    # Set up socket
    with socket.create_server(("localhost", 8080)) as server_socket:
        server_socket.listen(5)
        print("Server listening on: localhost on port: 8080")
        client_socket, addr = server_socket.accept()
        with client_socket:
            print(f"Connected by {addr}")
            print("Waiting for message...")
            do_long_prompt = True
            long_prompt = "Type /q to quit\nEnter message to send..."
            # Main loop
            while True:
                message_received = read_incoming_data(client_socket)
                if not message_received:
                    continue
                if message_received == "/q":
                    break
                print(message_received)
                do_long_prompt and print(long_prompt)
                do_long_prompt = False
                new_message = input(">")
                if new_message == "/q":
                    break
                send_outgoing_data(client_socket, new_message)


if __name__ == '__main__':
    main()
