import random
import socket
import threading
from p2p.SocketUtil import newServerSocket, recvObj
from core.Transaction import Tx
from core.TxBlock import TxBlock
from core.Signature import pubk_from_bytes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing import List, Tuple, Dict

class Server:

    def __init__(self):
        self.port = random.randint(5000, 5100)
        self.listener = "0.0.0.0"
        self.socket: socket = newServerSocket(self.listener, self.port)
        self.is_running = True
        self.tx_received: List[Tx] = []
        self.flags_received: List[Tuple[bytes, bytes, bool]]
        self.block_received: TxBlock
        self.addresses_received: List[str, RSAPublicKey]
        self.listener_thread = threading.Thread(target=self.receive_objects)
        self.listener_thread.start()

    def receive_objects(self):
        while self.is_running:
            buffer = recvObj(self.socket)
            if isinstance(buffer, Tx):
                self.tx_received.append(buffer)
            elif isinstance(buffer, TxBlock) and not self.block_received:
                self.block_received = buffer
            elif isinstance(buffer, Tuple[bytes, bytes, bool]):
                self.flags_received.append(buffer)
            elif isinstance(buffer, Dict[str, bytes]):
                for username in buffer:
                    pub_k = pubk_from_bytes(buffer[username])
                    self.addresses_received.append((username, pub_k))
            elif isinstance(buffer, Tuple[str, bytes]):
                pub_k = pubk_from_bytes(bytes)
                self.addresses_received.append((buffer[0], pub_k))


    def stop_server(self):
        self.is_running = False
        self.listener_thread.join()
        self.socket.close()