import os
import signal
import socket
import select

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Server:
    def __init__(self, host, port):
        # 1. Define host and port
        # 2. Create a socket
        # 3. Bind the socket to the host and port
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def start(self):
        # 1. Listen for incoming connections
        self.socket.listen()
        input_socket = [self.socket]
        while True:
            read_ready, write_ready, exception = select.select(input_socket, [], [])

            for sock in read_ready:
                if sock == self.socket:
                    # 2. Accept incoming connections
                    client_socket, client_address = self.socket.accept()
                    input_socket.append(client_socket)
                else:
                    # 3. Receive command and filename from client
                    data = sock.recv(1024).decode()
                    command, filename = data.split()

                    # 4. Check if the command is "download"
                    if command != "download":
                        sock.sendall(b"Unknown command")
                        continue

                    # 5. Check if the file exists
                    filepath = os.path.join(BASE_DIR, "files", filename)
                    if not os.path.exists(filepath):
                        sock.sendall(b"File doesn't exists")
                        input_socket.remove(sock)
                        sock.close()
                        continue

                    filesize = os.path.getsize(filepath)

                    # 6. Send the header to the client
                    header = f"file-name: {filename},\r\nfile-size: {filesize}\r\n\r\n"
                    sock.sendall(header.encode())

                    # 7. Send the file to the client
                    with open(filepath, "rb") as f:
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            sock.sendall(data)

                    # 8. Close the connection
                    sock.close()
                    input_socket.remove(sock)

def handler(signum, frame):
    raise Exception("end of time")

if __name__ == "__main__":
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(120)
    try:
        server = Server("127.0.0.1", 65432)
        server.start()
    except Exception as e:
        signal.alarm(0)
