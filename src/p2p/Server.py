import socket
from p2p.SocketUtil import newServerSocket, recvObj
from core.Transaction import Tx
from core.TxBlock import TxBlock
from core.Signature import pubk_from_bytes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from typing import List, Tuple, Dict, Set
from p2p.Response import Response
from p2p.Requests import RequestData, Request

class Server:

    def __init__(self):
        self.port = 5000
        self.listener = "0.0.0.0"
        self.socket: socket = newServerSocket(self.listener, self.port)
        self.is_running = True

        self.tx_received: List[Tx] = []
        self.flags_received: List[Tuple[Tuple[bytes, bytes, bool], bytes]] = []
        self.block_received: TxBlock = None
        self.addresses_received: List[Tuple[str, RSAPublicKey]] = []
        self.recipients_received: Set[str] = set()
        self.tx_cancels_received: List[Tx] = []
        self.received_responses: List[Tuple[Response, str]] = []
        self.received_requests: List[RequestData] = []

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
            elif self.is_flag(buffer):
                self.flags_received.append(buffer)
            elif self.is_tx_cancel(buffer):
                tx: Tx = buffer[0]
                self.tx_cancels_received.append(tx)
            elif self.is_response(buffer):
                self.received_responses.append(buffer)
            elif self.is_request(buffer):
                self.received_requests.append(buffer)

    def is_tx(self, buffer):
        return isinstance(buffer, Tx)

    def is_user(self, buffer):
        if isinstance(buffer, tuple) and len(buffer) == 2:
            return isinstance(buffer[0], str) and isinstance(buffer[1], bytes)
        return False

    def is_flag(self, buffer):
        if isinstance(buffer, tuple) and len(buffer) == 2:
            flag, block_hash = buffer
            if isinstance(block_hash, bytes) and isinstance(flag, tuple) and len(flag) == 3:
                return isinstance(flag[0], bytes) and isinstance(flag[1], bytes) and isinstance(flag[2], bool)
        return False


    def is_tx_cancel(self, buffer):
        if isinstance(buffer, tuple) and len(buffer) == 2:
            return isinstance(buffer[0], Tx) and isinstance(buffer[1], str)
        return False

    def is_response(self, buffer):
        return isinstance(buffer, Response)

    def is_request(self, buffer):
        return isinstance(buffer, RequestData)

    def add_recipients(self, address):
        self.recipients_received.add(address[0])