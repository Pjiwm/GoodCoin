import random
import socket
import threading
from p2p.SocketUtil import newServerSocket, recvObj
from core.Transaction import Tx
from core.TxBlock import TxBlock
from typing import List

class Server:

    def __init__(self):
        self.port = random.randint(5000, 5100)
        self.listener = "0.0.0.0"
        self.socket: socket = newServerSocket(self.listener, self.port)
        self.is_running = True
        self.tx_received: List[Tx] = []
        self.block_received: TxBlock
        self.listener_thread = threading.Thread(target=self.receive_objects)
        self.listener_thread.start()

    def receive_objects(self):
        while self.is_running:
            buffer = recvObj(self.socket)
            if isinstance(buffer, Tx):
                self.tx_received.append(buffer)
            elif isinstance(buffer, TxBlock) and not self.block_received:
                self.block_received = buffer

    def stop_server(self):
        self.is_running = False
        self.listener_thread.join()
        self.socket.close()