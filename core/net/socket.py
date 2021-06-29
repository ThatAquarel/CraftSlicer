import socket
import struct

HOST = "localhost"
PORT = 25568


def send(path: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    sock.sendall(struct.pack(">hi", 2, len(path)))
    sock.sendall(path.encode("UTF-8"))

    data = struct.unpack(">hi", sock.recv(6))
    sock.close()

    return data
