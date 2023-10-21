import heapq
from typing import List
# from Transaction import Tx
from core.Transaction import Tx

class TxPool:
    def __init__(self):
        self.transactions: List[Tx] = []

    def push(self, tx: Tx):
        reward_remainder = tx.calc_tx_fee()
        heapq.heappush(self.transactions, (reward_remainder, tx))

    def pop(self):
        if self.transactions:
            return heapq.heappop(self.transactions)[1]
        else:
            return None
