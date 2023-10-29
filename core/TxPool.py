import heapq
import pickle
from typing import List
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from core.Transaction import Tx
POOL_STORE_PATH = "data/txpool.dat"
TRASH_STORE_PATH = "data/txtrashpool.dat"


class TxPool:
    def __init__(self):
        self.transactions: List[Tx] = self.__load_from_disk()
        self.invalid_transactions: List[Tx] = self.__load_from_disk(
            TRASH_STORE_PATH)

    def push(self, tx: Tx):
        if tx.is_valid():
            heapq.heappush(self.transactions, tx)
            self.__write_to_disk()
            return "Successfully added transaction to pool."
        else:
            self.invalid_transactions.append(tx)
            self.__write_to_disk(TRASH_STORE_PATH)
            return "Transaction is invalid."

    def pop(self):
        if self.transactions:
            popped = heapq.heappop(self.transactions)
            self.__write_to_disk()
            return popped
        else:
            return None

    def remove_invalid(self, pubk: RSAPublicKey):
        prior_length = len(self.invalid_transactions)
        self.invalid_transactions = [
            tx for tx in self.invalid_transactions if not tx.is_tx_author(pubk)]
        if prior_length != len(self.invalid_transactions):
            self.__write_to_disk(TRASH_STORE_PATH)
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

    def __write_to_disk(self, path=POOL_STORE_PATH):
        file = open(path, 'wb')
        pickle.dump(self.transactions, file, -1)
        file.close()

    def __load_from_disk(self, path=POOL_STORE_PATH):
        try:
            file = open(path, 'rb')
            transactions = pickle.load(file)
            file.close()
            return transactions
        except:
            return []
