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
        return (pickle.loads(all_data), addr[0])
    return (None, None)


def sendObj(ip_addr, port, data):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((ip_addr, port))
    data = pickle.dumps(data)
    soc.send(data)
    soc.close()
    return False

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

local_ip = get_local_ip()