from core.Transaction import Tx
from core.TxBlock import TxBlock
from p2p.SocketUtil import sendObj
from typing import Tuple
class Client:

    def __init__(self):
        self.recipients = []

    def send_transaction(self, tx: Tx):
        self.__send_to_recipients(tx)

    def send_block(self, block: TxBlock):
        # make sure block has not prevBlock or flags
        block.previous_block = None
        block.valid_flags = []
        block.invalid_flags = []
        self.__send_to_recipients(block)

    def send_flag(self, flag: Tuple[bytes, bytes, bool]):
        self.__send_to_recipients(flag)

    def add_recipient(self, ip, port):
        self.recipients.append((ip, port))

    def __send_to_recipients(self, data):
        for rec in self.recipients:
            sendObj(rec[0], rec[1], data)