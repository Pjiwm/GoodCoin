from typing import List, Dict
from core.Transaction import Tx
from core.TxBlock import TxBlock
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

class Response:
    def __init__(self):
        pass

class BlockResponse (Response):
    block: TxBlock
    def __init__(self, block: TxBlock):
        self.block = block

class TxResponse (Response):
    transactions: List[Tx]
    def __init__(self, transactions: List[Tx]):
        self.transactions = transactions

class AdressBookResponse (Response):
    address_book: Dict[str, RSAPublicKey]
    def __init__(self, address_book: Dict[str, RSAPublicKey]):
        self.address_book = address_book
