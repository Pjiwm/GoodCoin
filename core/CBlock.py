from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from typing import NewType, List
from core.Transaction import Tx
CBlockSelf = NewType('CBlockSelf', 'CBlock')

class CBlock:

    data: List[Tx] = None
    previousHash: bytes = None
    blockHash: bytes = None
    previousBlock: CBlockSelf = None
    def __init__(self, data, previousBlock: CBlockSelf):
        self.data = data
        self.previousBlock = previousBlock
        if previousBlock != None:
            self.previousHash = previousBlock.computeHash()

    def computeHash(self) -> bytes:
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data),'utf8'))
        digest.update(bytes(str(self.previousHash),'utf8'))
        return digest.finalize()

    def is_valid(self):
        if self.previousBlock == None:
            return True
        return self.previousBlock.computeHash() == self.previousHash