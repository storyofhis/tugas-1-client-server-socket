import os
import socket
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class Client:
    def __init__(self, host, port):
        # 1. Define host and port
        # 2. Create a socket
        self.host = host
        self.port = port
        self.socket = socket.socket()

    def connect(self):
        # 3. Connect to the server
        self.socket.connect((self.host, self.port))

    def send_message(self, message):
        # 4. Send a message to the server
        # 5. Receive a response from the server and return it
        self.socket.sendall(message.encode())
        response = self.socket.recv(1024).decode()
        return response

    def recv(self, size):
        # 6. Receive data from the server and return it
        data = b''
        while b'\r\n\r\n' not in data:
            data += self.socket.recv(size)
        return data

    def disconnect(self):
        # 7. Close the connection
        self.socket.close()


    def parse_header(self, header):
        file_info = header.split(", ")
        file_name = file_info[0].split(": ")[1]
        file_size = int(file_info[1].split(": ")[1])
        return file_name, file_size

if __name__ == "__main__":
    # 1. Create a Client object
    client = Client("127.0.0.1", 65432)

    # 2. Connect to the server
    client.connect()

    # 3. Send a message to the server and receive a response
    message = input("Enter a message: ")
    status = client.send_message(message)
    print(status)

    # 4. Check if the response isn't a header
    # 4.1 If it is, print the response and exit
    if status.startswith("file-name:"):
        print(status)
        exit()

    # 5. Parse the header
    file_name, file_size = client.parse_header(status.encode())
    file_path = f"./{file_name}"

    # 6. Receive the file from the server and save it
    with open(file_path, "wb") as f:
        bytes_received = 0
        while bytes_received < file_size:
            data = client.recv(1024)
            f.write(data)
            bytes_received += len(data)

    # 7. Close the connection
    client.disconnect()