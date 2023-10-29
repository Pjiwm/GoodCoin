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

LEADING_ZEROS = 2
NEXT_CHAR_LIMIT = 20


class TxBlock (CBlock):
    id = 0
    miner = None
    nonce = "A random nonce"
    # RSAPublicKey, encrypted hash as bytes
    invalid_flags: List[Tuple[bytes, bytes]] = []
    valid_flags: List[Tuple[bytes, bytes]] = []

    def __init__(self, previousBlock: CBlockSelf, miner: RSAPublicKey):
            super(TxBlock, self).__init__([], previousBlock)
            self.id = previousBlock.id + 1 if previousBlock else 0
            self.miner = miner.public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo) if miner else None

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
            return False
        # Check Transactions
        for tx in self.data:
            if not tx.is_valid():
                return False
        # Check reward
        if self.invalid_reward():
            return False
        # Check if id is correct
        if self.invalid_id():
            return False

        # Check if tampered
        if self.block_hash:
            return self.__hash_nonce().hex() == self.block_hash.hex()
        return True

    def good_nonce(self):
        block_hash = self.__hash_nonce().hex()
        return block_hash[:LEADING_ZEROS] == '0' * LEADING_ZEROS

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
        return digest.finalize()
