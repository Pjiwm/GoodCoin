import heapq
import pickle
from typing import List
from core.Transaction import Tx
POOL_STORE_PATH = "data/txpool.dat"

class TxPool:
    def __init__(self):
        self.transactions: List[Tx] = self.__load_from_disk()

    def push(self, tx: Tx):
        reward_remainder = tx.calc_tx_fee()
        heapq.heappush(self.transactions, (reward_remainder, tx))
        self.__write_to_disk()

    def pop(self):
        if self.transactions:
            return heapq.heappop(self.transactions)[1]
        else:
            return None

    def __write_to_disk(self):
        file = open(POOL_STORE_PATH, 'wb')
        pickle.dump(self.transactions, file, -1)
        file.close()

    def __load_from_disk(self):
        try:
            file = open(POOL_STORE_PATH, 'rb')
            transactions = pickle.load(file)
            file.close()
            return transactions
        except:
            return []
