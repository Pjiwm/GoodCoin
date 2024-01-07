import socket
import pickle
import select
import ipaddress

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
        if is_local_connection(addr[0]):
            return (None, None)
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
    return 0

def is_local_connection(client_ip):
    # Get the local machine's IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    # Convert IP addresses to IPv4 objects for easy comparison
    client_ip = ipaddress.IPv4Address(client_ip)
    local_ip = ipaddress.IPv4Address(local_ip)
    # Check if the connection is from the same machine
    return client_ip == local_ip