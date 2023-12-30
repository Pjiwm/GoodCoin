from core.Transaction import Tx
from core.TxBlock import TxBlock
from p2p.SocketUtil import sendObj
from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
class Client:

    def __init__(self):
        self.recipients = []
        self.recipients.append("python_goodcoin")
        self.recipients.append("client2_goodcoin")

    def send_transaction(self, tx: Tx):
        self.__send_to_recipients(tx)

    def send_block(self, block: TxBlock):
        # make sure block has not prevBlock
        new_block = TxBlock(None, None)
        new_block.time_of_creation = block.time_of_creation
        new_block.nonce = block.nonce
        new_block.invalid_flags = block.invalid_flags
        new_block.valid_flags = block.valid_flags
        new_block.miner = block.miner
        new_block.previous_hash = block.previous_hash
        new_block.data = block.data
        new_block.block_hash = block.block_hash
        new_block.id = block.id
        self.__send_to_recipients(new_block)

    def send_flag(self, flag: Tuple[bytes, bytes, bool], block_hash: bytes):
        self.__send_to_recipients((flag, block_hash))

    def send_address_book(self, address_book: Dict[str, RSAPublicKey]):
        address_book_buffer = {}
        for username in address_book:
            address_book_buffer[username] = address_book[username].public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
        self.__send_to_recipients(address_book)

    def send_new_user(self, username: str, public_key: RSAPublicKey):
        public_bytes = public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
        self.__send_to_recipients((username, public_bytes))


    def add_recipient(self, ip):
        self.recipients.append(ip)

    def __send_to_recipients(self, data, port=5000):
        for address in self.recipients:
            try:
                sendObj(address, port, data)
            except:
                return