import re
from core import Signature
from core.TxPool import TxPool
from core.Transaction import Tx
from core.TxType import TxType
from core.TxBlock import TxBlock, REQUIRED_FLAG_COUNT
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from typing import Dict, List, Union
import pickle


class BlockchainManager:
    priv_key: RSAPrivateKey
    pub_k: RSAPublicKey
    tx_pool: TxPool
    username: str
    address_book: Dict[str, RSAPublicKey]
    block: TxBlock

    def __init__(self):
        Signature.create_data_folder_and_file()
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
        Signature.save_user_keys(username, key_set, pass_hash)
        self.priv_key, self.pub_k = key_set
        self.username = username
        self.address_book = Signature.load_address_book()
        return

    def login_user(self, username: str, pw: str):
        try:
            pass_hash = Signature.string_hash(pw)
            self.priv_key, self.pub_k = Signature.load_user_keys(
                username, pass_hash)
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

    def mine_block_optimal(self):
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

    def mine_block_manual(self, tx_list: List[Tx]):
        new_block = TxBlock(self.block, self.pub_k)
        for tx in tx_list:
            new_block.add_tx(self.tx_pool.take(tx))
        nonce = new_block.find_nonce()
        if new_block.good_nonce():
            self.block = new_block
            self.__store_block()
            return f"Mined new block {new_block.block_hash.hex()} with nonce: {nonce}"
        else:
            return f"Failed to mine block {new_block.block_hash.hex()} with nonce: {nonce}"

    def calculate_balance(self):
        return self.calculate_user_balance(self.pub_k)

    def calculate_user_balance(self, user: Union[bytes, RSAPublicKey]):
        if isinstance(user, RSAPublicKey):
            user = user.public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        last_valid_block = self.block
        while not last_valid_block.is_valid():
            last_valid_block = last_valid_block.previous_block
            if last_valid_block is None:
                break
        return self.block.user_balance(user)

    def add_flag_to_block(self):
        if self.block.previous_block is None:
            return

        my_pubk_bytes = self.pub_k.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        if my_pubk_bytes == self.block.miner:
            return

        result = None
        def check_flag(x): return any(
            my_pubk_bytes == pubk for pubk, _, _ in x)
        already_flagged = check_flag(
            self.block.invalid_flags) or check_flag(self.block.valid_flags)

        if not already_flagged:
            result = self.block.add_flag(self.priv_key, self.pub_k)
            self.__store_block()
            if len(self.block.valid_flags) == REQUIRED_FLAG_COUNT:
                self.__create_reward_tx()

        if len(self.block.invalid_flags) == REQUIRED_FLAG_COUNT:
            self.remove_last_block()
        return result

    def remove_last_block(self):
        for tx in self.block.data:
            self.tx_pool.push(tx)
        self.block = self.block.previous_block
        self.__store_block()

    def __create_reward_tx(self):
        reward_tx = Tx(type=TxType.Reward)
        reward_tx.add_output(self.block.miner, TxType.Reward.value + self.block.total_tx_fee())
        self.tx_pool.push(reward_tx)

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