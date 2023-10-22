import re
from core import Signature
from core.TxPool import TxPool
from core.Transaction import TxBuilder, Tx
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from typing import Dict


class BlockchainManager:
    priv_key: RSAPrivateKey
    pub_k: RSAPublicKey
    tx_pool: TxPool
    username: str
    address_book: Dict[str, RSAPublicKey]

    def __init__(self):
        self.priv_key = None
        self.pub_k = None
        self.username = None
        self.tx_pool = TxPool()
        self.address_book = Signature.load_address_book()

    def register_user(self, username: str, pw: str):
        if not Signature.username_available(username):
            return "Username already in use."

        if len(username) < 4 or len(pw) < 6 or not bool(re.search(r'\d', pw)):
            return "Username needs to be 5+ characters, password needs to be 6+ characters and contain a number."

        key_set = Signature.generate_keys()
        pass_hash = Signature.string_hash(pw)
        Signature.save_user_keys(username + ".pem", key_set, pass_hash)
        self.priv_key, self.pub_k = key_set
        self.username = username
        Signature.store_in_address_book(username, self.pub_k)
        self.address_book = Signature.load_address_book()
        return

    def login_user(self, username: str, pw: str):
        file_name = username + ".pem"
        try:
            pass_hash = Signature.string_hash(pw)
            self.priv_key, self.pub_k = Signature.load_user_keys(
                file_name, pass_hash)
            self.username = username
            return None
        except:
            return "Login failed, incorrect credentials."

    def logout_user(self):
        self.username = None
        self.priv_key = None
        self.pub_k = None

    def get_transaction_builder() -> TxBuilder:
        return TxBuilder()

    def make_transaction(tx: Tx):
        TxPool.push(tx)
