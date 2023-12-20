from core.Transaction import Tx
from core.TxBlock import TxBlock
from p2p.SocketUtil import sendObj
class Client:

    def __init__(self):
        self.recipients = []

    def send_transaction(self, tx: Tx):
        self.__send_to_recipients(tx)

    def send_block(self, block: TxBlock):
        # make sure block has not prevBlock
        block.previous_block = None
        self.__send_to_recipients(block)


    def add_recipient(self, ip, port):
        self.recipients.append((ip, port))

    def __send_to_recipients(self, data):
        for rec in self.recipients:
            sendObj(rec[0], rec[1], data)