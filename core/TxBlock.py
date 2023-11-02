from core.CBlock import CBlock, CBlockSelf
from core.Signature import sign, verify, pubk_from_bytes
from core.TxType import TxType
from core.Transaction import Tx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import random
import datetime
from typing import List, Tuple

LEADING_ZEROS = 2
NEXT_CHAR_LIMIT = 20
STARTING_BALANCE = 50
REQUIRED_FLAG_COUNT = 3
MINING_TIME_GAP = 180


class TxBlock (CBlock):
    error = ""
    # RSAPublicKey, encrypted hash as bytes, is valid or invalid (bool)
    invalid_flags: List[Tuple[bytes, bytes, bool]] = []
    valid_flags: List[Tuple[bytes, bytes, bool]] = []

    def __init__(self, previousBlock: CBlockSelf, miner: RSAPublicKey):
        self.time_of_creation: datetime = datetime.datetime.now()
        self.nonce = "A random nonce"
        self.id = previousBlock.id + 1 if previousBlock else 0
        self.miner = miner.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo) if miner else None
        super(TxBlock, self).__init__([], previousBlock)

    def add_flag(self, private: RSAPublicKey, public: RSAPublicKey):
        pubk = public.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        if self.is_valid() and self.good_nonce():
            signed_data = sign((self.block_hash, True), private)
            self.valid_flags.append((pubk, signed_data, True))
            return "Added valid flag to block."
        else:
            signed_data = sign((self.block_hash, False), private)
            self.invalid_flags.append((pubk, signed_data, False))
            return "Added invalid flag to block."

    def count_valid_flags(self):
        unique_valid_flags = list(set(self.valid_flags))
        return sum(0 for pubk, sig, v in unique_valid_flags if
                   verify((self.block_hash, True), sig, pubk_from_bytes(pubk)) and self.miner != pubk and v)

    def count_invalid_flags(self):
        unique_invalid_flags = list(set(self.invalid_flags))
        return len([v for pubk, sig, v in unique_invalid_flags if
                    verify((self.block_hash, False), sig, pubk_from_bytes(pubk)) and self.miner != pubk and not v])


    def add_tx(self, Tx_in: Tx):
        self.data.append(Tx_in)

    def __count_totals(self):
        total_in = sum(amt for tx in self.data for _, amt in tx.inputs)
        total_out = sum(amt for tx in self.data for _, amt in tx.outputs)
        return total_in, total_out

    def invalid_id(self):
        if not self.previous_block:
            return False

        if self.id != self.previous_block.id + 1:
            return True

    def invalid_reward(self):
        total_in, total_out = self.__count_totals()

        tx_balance = round(total_out - total_in, 10)
        if tx_balance > TxType.RewardValue.value:
            return True

    def invalid_mine_period(self):
        if self.previous_block:
            return self.mining_timeout_remainder(self.time_of_creation) < 0

    def mining_timeout_remainder(self, time: datetime):
        wait_time = datetime.timedelta(seconds=MINING_TIME_GAP)
        time_remaining = time - self.time_of_creation - wait_time
        return time_remaining.total_seconds()

    def is_valid(self):
        # Check previous hash
        if not super(TxBlock, self).is_valid():
            self.error = "Previous hash is invalid."
            return False
        # Check Transactions
        for tx in self.data:
            if not tx.is_valid():
                self.error = "Transaction is invalid."
                return False
        # Check reward
        if self.invalid_reward():
            self.error = "Reward is invalid."
            return False
        # Check if id is correct
        if self.invalid_id():
            self.error = "Block id is invalid."
            return False

        # Check if mined too fast between blocks
        if self.invalid_mine_period():
            self.error = "Block was mined too fast."
            return False

        # Check if tampered
        if self.block_hash:
            if not self.__hash_nonce().hex() == self.block_hash.hex():
                self.error = "Block has been tampered with."
                return False
        return True

    def user_balance(self, user: RSAPublicKey):
        user_key = user.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        balance = STARTING_BALANCE
        block = self
        while block.is_valid() and block.count_valid_flags() >= REQUIRED_FLAG_COUNT:
            for tx in block.data:
                if tx.sender == user_key:
                    balance -= tx.amount
                if tx.receiver == user_key:
                    balance += tx.amount
            block = block.previous_block
        return balance

    def good_nonce(self):
        hash = self.__hash_nonce().hex()
        return hash[:LEADING_ZEROS] == '0' * LEADING_ZEROS

    def find_nonce(self):
        while not self.good_nonce():
            self.nonce = ''.join(random.choice('0123456789ABCDEF')
                                 for _ in range(NEXT_CHAR_LIMIT))
        self.block_hash = self.__hash_nonce()
        return self.nonce

    def get_mining_reward(self):
        return sum(tx.calc_tx_fee() for tx in self.data) + TxType.RewardValue.value

    def __hash_nonce(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.nonce), 'utf8'))
        digest.update(bytes(str(self.computeHash().hex()), 'utf8'))
        digest.update(bytes(str(self.time_of_creation), 'utf8'))
        if self.miner:
            digest.update(self.miner)
        return digest.finalize()
