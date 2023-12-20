import socket
import pickle
import select

BUFFER_SIZE = 1024

def newServerSocket(ip_addr, port) -> socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_addr, port))
    server_socket.listen()
    return server_socket


def recvObj(socket):
    inputs, outputs, errs = select.select([socket], [], [socket], 6)
    if socket in inputs:
        connected_socket, addr = socket.accept()
        all_data = b''
        while True:
            data = connected_socket.recv(BUFFER_SIZE)
            if not data:
                break
            all_data = all_data + data
        return pickle.loads(all_data)
    return None


def sendObj(ip_addr, port, data):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((ip_addr, port))
    data = pickle.dumps(data)
    soc.send(data)
    soc.close()
    return False