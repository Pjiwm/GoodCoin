import re
from core import Signature
from core.TxPool import TxPool
from core.Transaction import Tx
from core.TxBlock import TxBlock
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from typing import Dict
import pickle
STARTED_BALANCE = 50
REQUIRED_VALID_FLAGS = 3
class BlockchainManager:
    priv_key: RSAPrivateKey
    pub_k: RSAPublicKey
    tx_pool: TxPool
    username: str
    address_book: Dict[str, RSAPublicKey]
    block: TxBlock

    def __init__(self):
        self.priv_key = None
        self.pub_k = None
        self.username = None
        self.tx_pool = TxPool()
        self.address_book = Signature.load_address_book()
        self.block = self.__load_block()

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

    def read_transaction(self, idx) -> Tx:
        result = self.tx_pool.transactions[idx]
        if result:
            return result
        return []

    def make_transaction(self, tx: Tx):
        self.tx_pool.push(tx)

    def get_block(self, prev_idx):
        block = self.block
        while prev_idx != 0:
            block = block.previous_block
            prev_idx -= 1
        return block

    def mine_block(self):
        if len(self.tx_pool.transactions) < 5:
            return "Not enough transactions in transaction pool to mine a new block."

        new_block = TxBlock(self.block, self.pub_k)
        while len(new_block.data) < 10:
            tx = self.tx_pool.pop()
            if not tx:
                break
            new_block.add_tx(tx)

        nonce = new_block.find_nonce()
        if new_block.good_nonce():
            self.block = new_block
            self.__store_block()
            return f"Mined new block {new_block.block_hash.hex()} with nonce: {nonce}"
        else:
            return f"Failed to mine block {new_block.block_hash.hex()} with nonce: {nonce}"

    def calculate_balance(self):
        return self.block.user_balance(self.pub_k)

    def __load_block(self):
        try:
            file = open("data/blockchain.dat", 'rb')
            block = pickle.load(file)
            file.close()
            return block
        except:
            # The Genesis Block
            genesis = TxBlock(None, None)
            genesis.find_nonce()
            return genesis

    def __store_block(self):
        file = open("data/blockchain.dat", 'wb')
        pickle.dump(self.block, file)
        file.close()