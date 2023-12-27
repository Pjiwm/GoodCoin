from core.Transaction import Tx
from core.TxBlock import TxBlock
from p2p.SocketUtil import sendObj
from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
class Client:

    def __init__(self):
        self.recipients = []

    def send_transaction(self, tx: Tx):
        self.__send_to_recipients(tx)

    def send_block(self, block: TxBlock):
        # make sure block has not prevBlock
        block.previous_block = None
        self.__send_to_recipients(block)

    def send_flag(self, flag: Tuple[bytes, bytes, bool]):
        self.__send_to_recipients(flag)

    def send_address_book(self, address_book: Dict[str, RSAPublicKey]):
        address_book_buffer = {}
        for username in address_book:
            address_book_buffer[username] = address_book[username].public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
        self.__send_to_recipients(address_book)

    def send_new_user(self, username: str, public_key: bytes):
        self.__send_to_recipients((username, public_key))

    def send_recipient(self, ip: str):
        self.__send_to_recipients("ip"+ip)

    def add_recipient(self, ip, port):
        self.recipients.append((ip, port))

    def __send_to_recipients(self, data):
        for rec in self.recipients:
            sendObj(rec[0], rec[1], data)