import unittest, socket
from chat_server import read_incoming_data


class TestReadIncomingData(unittest.TestCase):
    """
    Defines unit tests for the read_incoming_data function.
    """
    @classmethod
    def setUpClass(cls):
        # Set up server
        print("Setting up sockets.")
        cls.listener_socket = socket.create_server(('localhost', 8080))
        print("Server socket listening at localhost 8080")

        # Set up client connection
        cls.client_socket = socket.create_connection(('localhost', 8080))
        cls.server_socket = cls.listener_socket.accept()[0]
        print("Client connected at localhost 8080")

    @classmethod
    def tearDownClass(cls) -> None:
        print("Closing sockets.")
        cls.server_socket.close()
        print("Closed server socket.")
        cls.client_socket.close()
        print("Closed client socket.")
        cls.listener_socket.close()
        print("Closed listener socket.")

    def test_empty_string(self):
        input_string = b":0:"
        self.client_socket.sendall(input_string)
        result = read_incoming_data(self.server_socket)
        expected = ""
        self.assertEqual(expected, result)

    def test_short_string(self):
        input_string = b":12:hello world!"
        self.client_socket.sendall(input_string)
        result = read_incoming_data(self.server_socket)
        expected = "hello world!"
        self.assertEqual(expected, result)

    def test_long_string(self):
        with open("long_text.txt", "r") as long_text:
            input_text = long_text.readline()
            expected = input_text
            input_text = f":{len(input_text)}:{input_text}"
            self.client_socket.sendall(input_text.encode())
            result = read_incoming_data(self.server_socket)
            self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
