import socket
from chat_server import read_and_print, send_user_input, get_args


def main(host, port):
    # Set up socket
    with socket.create_connection((host, port)) as server_socket:
        print(f"Connected to: {host} on port: {port}")
        do_long_prompt = True

        # Main loop
        while True:
            if send_user_input(server_socket, do_long_prompt):
                break
            do_long_prompt = False
            if read_and_print(server_socket):
                break


if __name__ == '__main__':
    arg_host, arg_port = get_args("Start a chat client.")
    main(arg_host, arg_port)
