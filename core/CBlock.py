from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from typing import NewType, List
from core.Transaction import Tx
CBlockSelf = NewType('CBlockSelf', 'CBlock')

class CBlock:

    data: List[Tx] = None
    previous_hash: bytes = None
    block_hash: bytes = None
    previous_block: CBlockSelf = None
    def __init__(self, data, previousBlock: CBlockSelf):
        self.data = data
        self.previous_block = previousBlock
        if previousBlock != None:
            self.previous_hash = previousBlock.computeHash()

    def computeHash(self) -> bytes:
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.data),'utf8'))
        digest.update(bytes(str(self.previous_hash),'utf8'))
        return digest.finalize()

    def is_valid(self):
        if self.previous_block == None:
            return True
        return self.previous_block.computeHash() == self.previous_hash