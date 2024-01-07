from core.Transaction import Tx
from core.TxBlock import TxBlock
from p2p.SocketUtil import sendObj
from p2p.Requests import RequestData
from p2p.Response import Response
from typing import Tuple, Dict
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import os
class Client:
    def __init__(self):
        client = os.environ.get('CLIENT')
        self.recipients = []
        if client != "1":
            self.recipients.append("python_goodcoin")
        else:
            self.recipients.append("client2_goodcoin")

    def send_transaction(self, tx: Tx):
        return self.__send_to_recipients(tx)

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
        return self.__send_to_recipients(new_block)

    def send_flag(self, flag: Tuple[bytes, bytes, bool], block_hash: bytes):
        print(">>>>>>>>>>>>>>>>", block_hash.hex())
        return self.__send_to_recipients((flag, block_hash))

    def send_address_book(self, address_book: Dict[str, RSAPublicKey]):
        address_book_buffer = {}
        for username in address_book:
            address_book_buffer[username] = address_book[username].public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
        return self.__send_to_recipients(address_book)

    def send_new_user(self, username: str, public_key: RSAPublicKey):
        public_bytes = public_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
        return self.__send_to_recipients((username, public_bytes))

    def send_request(self, request: RequestData):
        return self.__send_to_first_available(request)

    def send_response(self, response: Response):
        return self.__send_to_recipients(response)

    def send_tx_cancel(self, tx: Tx):
        return self.__send_to_recipients((tx, "cancel"))

    def add_recipient(self, ip):
        self.recipients.append(ip)

    def __send_to_recipients(self, data, port=5000):
        for address in self.recipients:
            try:
                sendObj(address, port, data)
            except:
                return 2
        return 2

    def __send_to_first_available(self, data, port=5000):
        res = 0
        for address in self.recipients:
            try:
               res = sendObj(address, port, data)
               if res == 0:
                   return 0
            except:
                return 1
        return 2