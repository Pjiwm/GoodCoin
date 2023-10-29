from core.CBlock import CBlock, CBlockSelf
from core.Signature import sign, verify, pubk_from_bytes
from core.TxType import TxType
from core.Transaction import Tx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import random
from typing import List, Tuple

leading_zeros = 2
next_char_limit = 20


class TxBlock (CBlock):
    error = ""
    # RSAPublicKey, encrypted hash as bytes
    invalid_flags: List[Tuple[bytes, bytes]] = []
    valid_flags: List[Tuple[bytes, bytes]] = []

    def __init__(self, previousBlock: CBlockSelf, miner: RSAPublicKey):
        self.nonce = "A random nonce"
        self.id = previousBlock.id + 1 if previousBlock else 0
        self.miner = miner.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo) if miner else None
        super(TxBlock, self).__init__([], previousBlock)

    def add_flag(self, private: RSAPublicKey, public: RSAPublicKey):
        pubk = public.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
        signed_hash = sign(self.computeHash(), private)
        if self.is_valid() and self.good_nonce():
            self.valid_flags.append((pubk, signed_hash))
        else:
            self.invalid_flags.append((pubk, signed_hash))

    def count_valid_flags(self):
        return sum(1 for bytes, msg in self.valid_flags if verify(msg, pubk_from_bytes(bytes), self.computeHash()))

    def count_invalid_flags(self):
        return sum(1 for bytes, msg in self.invalid_flags if verify(msg, pubk_from_bytes(bytes), self.computeHash()))

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

        # Check if tampered
        if self.block_hash:
            if not self.__hash_nonce().hex() == self.block_hash.hex():
                self.error = "Block has been tampered with."
                return False
        return True

    def good_nonce(self):
        hash = self.__hash_nonce().hex()
        return hash[:leading_zeros] == '0' * leading_zeros

    def find_nonce(self):
        while not self.good_nonce():
            self.nonce = ''.join(random.choice('0123456789ABCDEF') for _ in range(next_char_limit))
        self.block_hash = self.__hash_nonce()
        return self.nonce

    def get_mining_reward(self):
        return sum(tx.calc_tx_fee() for tx in self.data) + TxType.RewardValue.value

    def __hash_nonce(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.nonce), 'utf8'))
        digest.update(bytes(str(self.computeHash().hex()), 'utf8'))
        return digest.finalize()
