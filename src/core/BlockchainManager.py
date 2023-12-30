import re
import threading
from core import Signature
from core.TxPool import TxPool
from core.Transaction import Tx
from core.TxType import TxType
from core.TxBlock import TxBlock, REQUIRED_FLAG_COUNT
from p2p.Client import Client
from p2p.Server import Server
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from typing import Dict, List, Union, Tuple
import pickle


class BlockchainManager:
    priv_key: RSAPrivateKey
    pub_k: RSAPublicKey
    tx_pool: TxPool
    username: str
    address_book: Dict[str, RSAPublicKey]
    block: TxBlock
    server: Server
    client: Client

    def __init__(self):
        Signature.create_data_folder_and_file()
        self.priv_key = None
        self.pub_k = None
        self.username = None
        self.tx_pool = TxPool()
        self.address_book = Signature.load_address_book()
        self.block = self.__load_block()
        self.__store_block()
        self.server = Server()
        self.client = Client()
        self.server_listener_thread = threading.Thread(target=self.populate_from_server)
        self.server_listener_thread.start()

    def register_user(self, username: str, pw: str):
        if not Signature.username_available(username):
            return "Username already in use."

        if len(username) < 4 or len(pw) < 6 or not bool(re.search(r'\d', pw)):
            return "Username needs to be 5+ characters, password needs to be 6+ characters and contain a number."

        key_set = Signature.generate_keys()
        pass_hash = Signature.string_hash(pw)
        Signature.save_user_keys(username, key_set, pass_hash)
        Signature.store_in_address_book(username, key_set[1])
        self.client.send_new_user(username, key_set[1])
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

    def cancel_transaction(self, pub_key: RSAPublicKey, tx: Tx):
        result = self.tx_pool.cancel_transaction(pub_key, tx)
        if result == "Transaction has been canceled.":
            self.client.send_tx_cancel(tx)



    def make_transaction(self, tx: Tx):
        self.tx_pool.push(tx)
        self.client.send_transaction(tx)

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
            self.client.send_block(new_block)
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
            self.client.send_block(new_block)
            return f"Mined new block {new_block.block_hash.hex()} with nonce: {nonce}"
        else:
            return f"Failed to mine block {new_block.block_hash.hex()} with nonce: {nonce}"

    def calculate_balance(self):
        return self.calculate_user_balance(self.pub_k)  - self.calculate_pool_spendings()

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

    def calculate_pool_spendings(self):
        my_pubk_bytes = self.pub_k.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        spendings = 0
        for tx in self.tx_pool.transactions:
            for input in tx.inputs:
                if input[0] == my_pubk_bytes:
                    spendings += input[1]
        return spendings

    def add_flag_to_block(self):
        self.add_flag_to_specific_block(self.block, True)

    def add_flag_to_specific_block(self, block: TxBlock, is_last_block=False):
        hash = block.computeHash()
        if block.previous_block is None:
            return

        my_pubk_bytes = self.pub_k.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        if my_pubk_bytes == block.miner:
            return

        flag = None

        def check_flag(x): return any(
            my_pubk_bytes == pubk for pubk, _, _ in x)
        already_flagged = check_flag(
            block.invalid_flags) or check_flag(block.valid_flags)

        if not already_flagged:
            flag = block.add_flag(self.priv_key, self.pub_k)
            self.client.send_flag(flag, hash)
            self.__store_block()
            if len(block.valid_flags) == REQUIRED_FLAG_COUNT and is_last_block:
                self.__create_reward_tx(hash)

        if len(block.invalid_flags) == REQUIRED_FLAG_COUNT and is_last_block:
            self.remove_last_block()
        return (flag, hash)

    def remove_last_block(self):
        for tx in self.block.data:
            self.tx_pool.push(tx)
        self.block = self.block.previous_block
        self.__store_block()

    def __create_reward_tx(self, hash: bytes):
        reward_tx = Tx(type=TxType.Reward, uuid=hash)
        reward_tx.add_output(self.block.miner, TxType.Reward.value + self.block.total_tx_fee())
        self.tx_pool.push(reward_tx)
        # self.client.send_transaction(reward_tx)

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

    def populate_from_server(self):
        while self.server.is_running:
            self.server.receive_objects()
            if self.server.addresses_received:
                for username, pub_k in self.server.addresses_received:
                    self.address_book[username] = pub_k
                    Signature.store_in_address_book(username, pub_k)
                    self.server.addresses_received.remove((username, pub_k))
            if self.server.tx_received:
                for tx in self.server.tx_received:
                    self.tx_pool.push(tx)
                    self.server.tx_received.remove(tx)
            if self.server.block_received:
                new_block = self.server.block_received
                self.server.block_received = None
                prev_block = self.block
                if new_block.previous_hash == self.block.computeHash():
                    self.block = new_block
                    self.block.previous_block = prev_block
                    self.__store_block()
                    self.__removed_ledger_txs_from_pool()
                    # Remove used txs from pool.
            if self.server.flags_received:
                    buffer: List[Tuple[Tuple[bytes, bytes, bool], bytes]] = []
                    for item in self.server.flags_received:
                        buffer.append(item)
                        self.server.flags_received.remove(item)

                    for flag, block_hash in buffer:
                        # find block:
                        curr_block = self.block
                        while curr_block:
                            if curr_block.computeHash() == block_hash:
                                curr_block.add_external_flag(flag)
                                curr_block = None
                                if len(self.block.valid_flags) == REQUIRED_FLAG_COUNT:
                                    self.__create_reward_tx(hash=self.block.computeHash())
                            else:
                                curr_block = curr_block.previous_block
            if self.server.tx_cancels_received:
                for tx in self.server.tx_cancels_received:
                    for pool_tx in self.tx_pool.transactions:
                        if pool_tx == tx:
                            self.tx_pool.take(tx)
                            self.server.tx_cancels_received.remove(tx)



    def __removed_ledger_txs_from_pool(self):
        block_txs: List[Tx] = self.block.data
        for tx in block_txs:
            for pool_tx in self.tx_pool.transactions:
                # if tx.compare_uuid(pool_tx):
                #     self.tx_pool.take(pool_tx)
                if tx == pool_tx:
                    self.tx_pool.take(pool_tx)

    def stop_server(self):
        self.server.is_running = False
        self.server.socket.close()