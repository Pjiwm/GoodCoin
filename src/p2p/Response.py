from typing import List, Dict
from core.Transaction import Tx
from core.TxBlock import TxBlock
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from core.Signature import pubk_from_bytes
class Response:
    def __init__(self):
        pass

class BlockResponse (Response):
    block: TxBlock
    def __init__(self, block: TxBlock):
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
        self.block = new_block

class TxResponse (Response):
    transactions: List[Tx]
    def __init__(self, transactions: List[Tx]):
        self.transactions = transactions

class AdressBookResponse (Response):
    address_book: Dict[str, bytes]
    def __init__(self, address_book: Dict[str, RSAPublicKey]):
        self.address_book = self.__transform_dict(address_book)

    def __transform_dict(self, dict: Dict[str, RSAPublicKey]):
        address_book_buffer = {}
        for username in dict:
            address_book_buffer[username] = dict[username].public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
        return address_book_buffer

    def get_dictionary(self):
        address_book_buffer = {}
        for username in self.address_book:
            address_book_buffer[username] = pubk_from_bytes(self.address_book[username])
        return address_book_buffer
