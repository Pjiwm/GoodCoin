import heapq
import pickle
from typing import List
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from core.Transaction import Tx
from core.TxType import TxType
POOL_STORE_PATH = "data/txpool.dat"
TRASH_STORE_PATH = "data/txtrashpool.dat"


class TxPool:
    def __init__(self):
        valid, invalid = self.__load_from_disk()
        self.transactions: List[Tx] = valid
        self.invalid_transactions: List[Tx] = invalid

    def push(self, tx: Tx):
        if tx.is_valid():
            heapq.heappush(self.transactions, tx)
            self.__write_to_disk()
            return "Successfully added transaction to pool."
        else:
            self.invalid_transactions.append(tx)
            self.__write_to_disk()
            return "Transaction is invalid."

    def pop(self):
        if self.transactions:
            popped = heapq.heappop(self.transactions)
            self.__write_to_disk()
            return popped
        else:
            return None

    def take(self, tx: Tx):
        if tx in self.transactions:
            self.transactions.remove(tx)
            self.__write_to_disk()
            return tx
        else:
            return None

    def remove_invalid(self, pubk: RSAPublicKey):
        prior_length = len(self.invalid_transactions)
        self.invalid_transactions = [
            tx for tx in self.invalid_transactions if not tx.is_tx_author(pubk)]
        if prior_length != len(self.invalid_transactions):
            self.__write_to_disk()
            return "You've made some invalid transactions. They have been removed from the pool."
        return ""

    def cancel_transaction(self, pubk: RSAPublicKey, tx_to_cancel: Tx):
        for tx in self.transactions:
            if tx.is_tx_author(pubk) and tx_to_cancel == tx :
                self.transactions.remove(tx)
                self.__write_to_disk()
                return "Transaction has been canceled."
        return "Transaction not found or you don't have permission to cancel it."

    def get_users_txs(self, pubk: RSAPublicKey):
        return [tx for tx in self.transactions if tx.is_tx_author(pubk)]

    def get_reward_tx(self):
        for tx in self.transactions:
            if tx.type == TxType.Reward:
                return tx
        return None

    def __write_to_disk(self):
        file = open(POOL_STORE_PATH, 'wb')
        pickle.dump((self.transactions, self.invalid_transactions), file, -1)
        file.close()

    def __load_from_disk(self):
        try:
            file = open(POOL_STORE_PATH, 'rb')
            pool_data = pickle.load(file)
            file.close()
            return pool_data
        except:
            return ([],[])
