import socket
from chat_server import ChatSocket, get_args


def main(host, port):
    # Set up socket
    with socket.create_connection((host, port)) as server_socket:
        print(f"Connected to: {host} on port: {port}")
        do_long_prompt = True
        chatter = ChatSocket(server_socket)

        # Main loop
        while True:
            if chatter.send_user_input(do_long_prompt):
                break
            do_long_prompt = False
            if chatter.read_and_print():
                break


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat client.")
    main(arg_host, arg_port)
