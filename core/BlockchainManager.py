import re
from core import Signature
from core.TxPool import TxPool
from core.Transaction import TxBuilder, Tx
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


class BlockchainManager:
    priv_key: RSAPrivateKey
    pub_k: RSAPublicKey
    tx_pool: TxPool
    username: str

    def __init__(self):
        self.priv_key = None
        self.pub_k = None
        self.username = None
        self.tx_pool = TxPool()

    def register_user(self, username: str, pw: str):
        if not Signature.username_available(username):
            return "Username already in use."

        if len(username) < 4 or len(pw) < 6 or not bool(re.search(r'\d', pw)):
            return "Username needs to be 5+ characters, password needs to be 6+ characters and contain a number."

        key_set = Signature.generate_keys()
        Signature.save_keys(username + ".pem", key_set, pw)
        self.priv_key, self.pub_k = key_set
        self.username = username
        return

    def login_user(self, username: str, pw: str):
        file_name = username + ".pem"
        try:
            self.priv_key, self.pub_k = Signature.load_keys(file_name, pw)
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
