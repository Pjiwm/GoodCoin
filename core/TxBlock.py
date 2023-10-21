from CBlock import CBlock, CBlockSelf
from Signature import generate_keys, sign, verify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from TxType import TxType
from Transaction import Tx
import random

LEADING_ZEROS = 2
NEXT_CHAR_LIMIT = 20


class TxBlock (CBlock):

    def __init__(self, previousBlock: CBlockSelf):
        self.nonce = "A random nonce"
        super(TxBlock, self).__init__([], previousBlock)

    def addTx(self, Tx_in: Tx):
        self.data.append(Tx_in)

    def __count_totals(self):
        total_in = sum(amt for tx in self.data for _, amt in tx.inputs)
        total_out = sum(amt for tx in self.data for _, amt in tx.outputs)
        return total_in, total_out

    def invalid_reward(self):
        total_in, total_out = self.__count_totals()

        tx_balance = round(total_out - total_in, 10)
        if tx_balance > TxType.RewardValue:
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

        # Check if tampered
        if self.blockHash:
            return self.__hash_nonce().hex() == self.blockHash.hex()
        return True

    def good_nonce(self):
        block_hash = self.__hash_nonce().hex()
        return block_hash[:LEADING_ZEROS] == '0' * LEADING_ZEROS

    def find_nonce(self):
        while not self.good_nonce():
            self.nonce = ''.join(random.choice('0123456789ABCDEF')
                                 for _ in range(NEXT_CHAR_LIMIT))
        self.blockHash = self.__hash_nonce()
        return self.nonce

    def __hash_nonce(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.nonce), 'utf8'))
        digest.update(bytes(str(self.computeHash().hex()), 'utf8'))
        return digest.finalize()
