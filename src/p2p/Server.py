import socket
from p2p.SocketUtil import newServerSocket, recvObj
from core.Transaction import Tx
from core.TxBlock import TxBlock
from core.Signature import pubk_from_bytes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing import List, Tuple, Dict, Set

class Server:

    def __init__(self):
        self.port = 5000
        self.listener = "0.0.0.0"
        self.socket: socket = newServerSocket(self.listener, self.port)
        self.is_running = True

        self.tx_received: List[Tx] = []
        self.flags_received: List[Tuple[bytes, bytes, bool]] = []
        self.block_received: TxBlock = None
        self.addresses_received: List[Tuple[str, RSAPublicKey]] = []
        self.recipients_received: Set[str] = set()

    def receive_objects(self):
            buffer, addr = recvObj(self.socket)
            if not buffer:
                return
            if addr:
                self.add_recipients(addr)

            if self.is_tx(buffer):
                self.tx_received.append(buffer)
            elif self.is_user(buffer):
                pub_k = pubk_from_bytes(buffer[1])
                self.addresses_received.append((buffer[0], pub_k))
            elif isinstance(buffer, TxBlock) and not self.block_received:
                self.block_received = buffer
            elif isinstance(buffer, Tuple[bytes, bytes, bool]):
                self.flags_received.append(buffer)
            elif isinstance(buffer, Dict[str, bytes]):
                for username in buffer:
                    pub_k = pubk_from_bytes(buffer[username])
                    self.addresses_received.append((username, pub_k))

    def is_tx(self, buffer):
        return isinstance(buffer, Tx)

    def is_user(self, buffer):
        return isinstance(buffer, tuple) and len(buffer) == 2 and isinstance(buffer[0], str) and isinstance(buffer[1], bytes)


    def add_recipients(self, address):
        self.recipients_received.add(address[0])